import unittest
from unittest.mock import patch, MagicMock
from image_gui_cli import generate_key, encode_image_cli, decode_image_cli
from cryptography.fernet import Fernet

class TestSteganographyCLI(unittest.TestCase):
    
    def setUp(self):
        # Test data
        self.password = "testpassword"
        self.test_image = "test_image.png"
        self.test_message = "This is a test message"
        self.encoded_image = "test_image_encoded.png"

    
    def test_generate_key(self):
        key = generate_key(self.password)  # Pass the password to the generate_key function
        self.assertIsInstance(key, bytes)
        self.assertEqual(len(key), 44)      
        

    
    @patch('stegano.lsb.hide')
    def test_encode_image_cli(self, mock_hide):
        # Mock the save method of lsb.hide
        mock_hide.return_value.save = MagicMock()
        
        # Run the function to encode the image
        encode_image_cli(self.test_image, self.test_message, self.password)
        
        # Get the actual call arguments for lsb.hide
        args, kwargs = mock_hide.call_args
        actual_image = args[0]
        actual_encrypted_message = args[1]

        print(f"Actual encrypted message: {actual_encrypted_message}")

        # Since we cannot predict the exact encrypted message, check if hide is called with correct arguments
        self.assertEqual(actual_image, self.test_image)
        self.assertIsInstance(actual_encrypted_message, str)
        # Ensure the save method was called to save the image
        mock_hide.return_value.save.assert_called_once_with(self.test_image.rsplit('.', 1)[0] + '_encoded.png')

    @patch('stegano.lsb.reveal', return_value='gAAAAABmuWBEyO4ZABnvmSgF4ggztsjGbVwbS9afE-KAX7WHvFxGJzguLSkpLlP_uq59oCKVNQApN2gjQdcSkX5PTYQXBsC-SOkJmGfeBX6e3pyZ7hJWUWE=')
    @patch('cryptography.fernet.Fernet.decrypt', return_value=b'This is a test message')
    def test_decode_image_cli(self, mock_decrypt, mock_reveal):
        decode_image_cli(self.encoded_image, self.password)
        
        # Ensure lsb.reveal was called with the correct parameters
        mock_reveal.assert_called_once_with(self.encoded_image)
        # Ensure Fernet.decrypt was called with the correct encrypted message
        mock_decrypt.assert_called_once_with('gAAAAABmuWBEyO4ZABnvmSgF4ggztsjGbVwbS9afE-KAX7WHvFxGJzguLSkpLlP_uq59oCKVNQApN2gjQdcSkX5PTYQXBsC-SOkJmGfeBX6e3pyZ7hJWUWE='.encode('utf-8'))

if __name__ == "__main__":
    unittest.main()
