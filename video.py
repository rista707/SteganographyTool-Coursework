import argparse
import cv2
import numpy as np
from stegano import lsb
from PIL import Image
import os
import zlib
from base64 import b64encode, b64decode
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
import base64

def encrypt_message(message, password):
    salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    cipher = Fernet(key)
    encrypted_data = cipher.encrypt(message.encode())
    return salt + encrypted_data

def decrypt_message(encrypted_data, password):
    try:
        salt = encrypted_data[:16]
        encrypted_data = encrypted_data[16:]
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        cipher = Fernet(key)
        decrypted_data = cipher.decrypt(encrypted_data)
        return decrypted_data.decode()
    except Exception as e:
        print(f"Decryption error: {e}")
        return None

def compress_message(message):
    compressed_data = zlib.compress(message.encode())
    return b64encode(compressed_data).decode()

def decompress_message(compressed_base64_message):
    try:
        compressed_data = b64decode(compressed_base64_message.encode())
        return zlib.decompress(compressed_data).decode()
    except Exception as e:
        print(f"Decompression error: {e}")
        return None

def frame_to_pil_image(frame):
    return Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

def pil_image_to_opencv(pil_img):
    return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

def hide_data_in_video(input_video_path, output_video_path, frame_rate, frame_width, frame_height, codec, message, password):
    try:
        cap = cv2.VideoCapture(input_video_path)
        if not cap.isOpened():
            raise Exception(f"Error opening input video file {input_video_path}.")

        out = cv2.VideoWriter(output_video_path, codec, frame_rate, (frame_width, frame_height))
        if not out.isOpened():
            cap.release()
            raise Exception(f"Could not open VideoWriter with the specified codec or output file path: {output_video_path}")

        encrypted_message = encrypt_message(message, password)
        compressed_message = compress_message(encrypted_message.decode('latin1'))

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            pil_img = frame_to_pil_image(frame)
            secret_pil_img = lsb.hide(pil_img, compressed_message)
            frame = pil_image_to_opencv(secret_pil_img)
            out.write(frame)

        cap.release()
        out.release()

          # Confirmation message
        print(f"Message successfully hidden in {output_video_path}.")
    except Exception as e:
        print(f"Error hiding data in video: {e}")
        
    #except Exception as e:
        #print(f"Error hiding data in video: {e}")


def unhide_data_from_video(video_path, password):
    try:
        cap = cv2.VideoCapture(video_path)
        decoded_messages = []

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            pil_img = frame_to_pil_image(frame)
            compressed_base64_message_chunk = lsb.reveal(pil_img)

            if compressed_base64_message_chunk:
                decoded_message = decompress_message(compressed_base64_message_chunk)
                if decoded_message:
                    decoded_messages.append(decoded_message)

        cap.release()
        hidden_message = ''.join(decoded_messages)
        return decrypt_message(hidden_message.encode('latin1'), password)
    except Exception as e:
        print(f"Error unhiding data from video: {e}")
        return None
    
def main():
    parser = argparse.ArgumentParser(description='Simple LSB Steganography Tool for Video Files')

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Subparser for hiding data
    hide_parser = subparsers.add_parser('hide', help='Hide a message in a video file')
    hide_parser.add_argument('input_video', help='Path to the input video file')
    hide_parser.add_argument('output_video', help='Path to save the output video file with the hidden message')
    hide_parser.add_argument('message', help='Message to hide in the video')
    hide_parser.add_argument('password', help='Password for encrypting the message')

    # Subparser for unhiding data
    unhide_parser = subparsers.add_parser('unhide', help='Unhide a message from a video file')
    unhide_parser.add_argument('video', help='Path to the video file with the hidden message')
    unhide_parser.add_argument('password', help='Password for decrypting the hidden message')

    args = parser.parse_args()

    if args.command == 'hide':
        # Open the video to get frame rate, width, height, and codec information
        cap = cv2.VideoCapture(args.input_video)
        if not cap.isOpened():
            print(f"Error opening video file {args.input_video}.")
            return

        frame_rate = int(cap.get(cv2.CAP_PROP_FPS))
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        codec = cv2.VideoWriter_fourcc(*'XVID')
        codec = cv2.VideoWriter_fourcc(*'mp4v')

        cap.release()

        hide_data_in_video(args.input_video, args.output_video, frame_rate, frame_width, frame_height, codec, args.message, args.password)
    elif args.command == 'unhide':
        decrypted_message = unhide_data_from_video(args.video, args.password)
        if decrypted_message:
            print(f"Decrypted Message: {decrypted_message}")
        else:
            print("Failed to decrypt the message or no hidden message found.")
    else:
        parser.print_help()


if __name__ == '__main__':
    main() 