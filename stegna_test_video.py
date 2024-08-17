import unittest
from unittest.mock import patch, MagicMock
import numpy as np
from video import (
    encrypt_message, decrypt_message, compress_message, decompress_message,
    hide_data_in_video, unhide_data_from_video, frame_to_pil_image, pil_image_to_opencv
)
from PIL import Image
import cv2

class TestStegoVideo(unittest.TestCase):

    def setUp(self):
        self.message = "This is a secret message."
        self.password = "strong_password"
        self.compressed_message = compress_message(self.message)
        self.encrypted_message = encrypt_message(self.message, self.password)

    def test_encrypt_decrypt_message(self):
        encrypted = encrypt_message(self.message, self.password)
        decrypted = decrypt_message(encrypted, self.password)
        self.assertEqual(decrypted, self.message)

    def test_compress_decompress_message(self):
        compressed = compress_message(self.message)
        decompressed = decompress_message(compressed)
        self.assertEqual(decompressed, self.message)

    def test_encrypt_message_error(self):
        wrong_password = "wrong_password"
        decrypted = decrypt_message(self.encrypted_message, wrong_password)
        self.assertIsNone(decrypted)

    def test_frame_to_pil_image(self):
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        pil_image = frame_to_pil_image(frame)
        self.assertIsInstance(pil_image, Image.Image)

    def test_pil_image_to_opencv(self):
        pil_img = Image.new('RGB', (640, 480))
        opencv_frame = pil_image_to_opencv(pil_img)
        self.assertIsInstance(opencv_frame, np.ndarray)

    @patch('cv2.VideoCapture')
    @patch('cv2.VideoWriter')
    @patch('stegano.lsb.hide')
    def test_hide_data_in_video(self, mock_hide, mock_video_writer, mock_video_capture):
        # Mocking video processing functions
        mock_cap = MagicMock()
        mock_video_capture.return_value = mock_cap
        mock_cap.isOpened.return_value = True
        mock_cap.read.side_effect = [(True, np.zeros((480, 640, 3), dtype=np.uint8)), (False, None)]  # Valid frame followed by end

        mock_out = MagicMock()
        mock_video_writer.return_value = mock_out

        # Mock the hide function to simulate successful hiding
        mock_hide.return_value = MagicMock()

        try:
            hide_data_in_video("input.mp4", "output.mp4", 30, 640, 480, 'XVID', self.message, self.password)
        except Exception as e:
            self.fail(f"Exception during hide_data_in_video: {e}")

        # Ensure that the VideoWriter.write was called with a valid frame
        self.assertTrue(mock_out.write.called, "VideoWriter.write was not called.")

    @patch('cv2.VideoCapture')
    @patch('stegano.lsb.reveal')
    def test_unhide_data_from_video(self, mock_reveal, mock_video_capture):
        mock_cap = MagicMock()
        mock_video_capture.return_value = mock_cap
        mock_cap.isOpened.return_value = True
        mock_cap.read.side_effect = [(True, np.zeros((480, 640, 3), dtype=np.uint8)), (False, None)]

        # Mock the reveal function to return the compressed message
        mock_reveal.return_value = self.compressed_message

        decrypted_message = None
        try:
            compressed_message = unhide_data_from_video("input.mp4", self.password)
            if compressed_message:
                decrypted_message = decompress_message(compressed_message)
        except Exception as e:
            self.fail(f"Exception during unhide_data_from_video: {e}")

        # Ensure the message is successfully decrypted
        self.assertEqual(decrypted_message, self.message, "The decrypted message does not match the original.")

if __name__ == '__main__':
    unittest.main()
