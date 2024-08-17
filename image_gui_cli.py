import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import customtkinter as ctk
from stegano import lsb
from cryptography.fernet import Fernet
import base64
import argparse

class SteganographyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Steganography Tool")
        self.center_window(800, 600)

        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("dark-blue")

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("Treeview.Heading", font=("Helvetica", 14, "bold"), background="#2e2e2e", foreground="#d3d3d3")
        self.style.configure("Treeview", font=("Helvetica", 12), rowheight=24, background="#2e2e2e", fieldbackground="#2e2e2e", foreground="#d3d3d3")
        self.style.map("Treeview", background=[("selected", "#3e3e3e")], foreground=[("selected", "white")])

        # Store image reference to prevent garbage collection
        self.image_photo = None

        self.create_widgets()
        self.setup_layout()

    def center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = int((screen_width / 1.43) - (800 / 1.5))
        y = int((screen_height / 1.75) - (600 / 1.5))
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def create_widgets(self):
        # Title with icon
        self.title_frame = ctk.CTkFrame(self.root, corner_radius=20, fg_color="#2e2e2e")
        self.title_label = ctk.CTkLabel(self.title_frame, text="  Image Steganography Tool", font=("Helvetica", 18, "bold"))

        self.encode_button = ctk.CTkButton(self.root, text="Encode Message", command=self.encode_message, width=150)
        self.decode_button = ctk.CTkButton(self.root, text="Decode Message", command=self.decode_message, width=150)

        # File selection
        self.file_label = ctk.CTkLabel(self.root, text="Select File")
        self.file_entry = ctk.CTkEntry(self.root, width=200, state='readonly')  # Make it readonly
        self.browse_button = ctk.CTkButton(self.root, text="Browse", command=self.browse_file, width=100)

        # Message entry
        self.message_label = ctk.CTkLabel(self.root, text="Enter Message")
        self.message_text = tk.Text(self.root, wrap='word', height=8, width=40, bg='#2e2e2e', fg='#d3d3d3', insertbackground='white', font=("Helvetica", 16))

        # Password entry
        self.password_label = ctk.CTkLabel(self.root, text="Enter Password")
        self.password_entry = ctk.CTkEntry(self.root, width=200, show='*')

        # Image display
        self.image_label = ctk.CTkLabel(self.root, text="No image selected", image=None)

        # Results display
        self.results_label = ctk.CTkLabel(self.root, text="Decoded Message")
        self.results_text = tk.Text(self.root, wrap='word', state='disabled', height=3, width=40, bg='#2e2e2e', fg='#d3d3d3', insertbackground='white', font=("Helvetica", 16))
        self.results_scroll = ctk.CTkScrollbar(self.root, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=self.results_scroll.set)

    def setup_layout(self):
        # Layout for title
        self.title_frame.grid(column=0, row=0, columnspan=3, padx=10, pady=10, sticky='ew')
        self.title_label.grid(column=0, row=0, padx=10, pady=5, sticky='w')
        self.title_frame.grid_columnconfigure(1, weight=1)

        self.file_label.grid(column=0, row=1, padx=10, pady=5, sticky='w')
        self.file_entry.grid(column=1, row=1, padx=5, pady=5, sticky='ew')
        self.browse_button.grid(column=2, row=1, padx=10, pady=5, sticky='ew')

        self.message_label.grid(column=0, row=2, padx=10, pady=5, sticky='w')
        self.message_text.grid(column=0, row=3, padx=10, pady=5, columnspan=3, sticky='nsew')

        self.password_label.grid(column=0, row=4, padx=10, pady=5, sticky='w')
        self.password_entry.grid(column=1, row=4, padx=5, pady=5, sticky='ew')

        self.encode_button.grid(column=0, row=5, padx=10, pady=10, sticky='ew')
        self.decode_button.grid(column=1, row=5, padx=5, pady=10, sticky='ew')

        self.image_label.grid(column=0, row=6, padx=10, pady=5, columnspan=3, sticky='nsew')

        self.results_label.grid(column=0, row=7, padx=10, pady=5, sticky='w')
        self.results_text.grid(column=0, row=8, padx=10, pady=5, columnspan=3, sticky='nsew')
        self.results_scroll.grid(column=3, row=8, sticky='ns')

        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(8, weight=1)

    def browse_file(self):
        file_path = filedialog.askopenfilename(title="Select File", filetypes=(
            ("Image Files", "*.png;*.jpg;*.jpeg"), 
            ))
        
        if file_path:
            self.file_entry.configure(state='normal')  # Allow writing to entry
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, file_path)
            self.file_entry.configure(state='readonly')  # Set back to readonly

            # Determine the file type and display accordingly
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                self.display_image(file_path)

    def display_image(self, file_path):
        try:
            # Open the image file
            image = Image.open(file_path)
            
            # Resize the image for display
            image.thumbnail((100, 80), Image.LANCZOS)
            
            # Convert the image to a format Tkinter can use
            self.image_photo = ImageTk.PhotoImage(image)
            
            # Update the image label to display the image
            self.image_label.configure(image=self.image_photo, text="")
            
        except Exception as e:
            messagebox.showerror("Image Error", f"Could not display image: {str(e)}")
            self.image_label.configure(image=None, text="No image selected")

    def encode_message(self):
        file_path = self.file_entry.get().strip()
        message = self.message_text.get("1.0", tk.END).strip()
        password = self.password_entry.get().strip()
        if not file_path or not message or not password:
            messagebox.showerror("Error", "Please select a file, enter a message, and provide a password.")
            return

        try:
            # Generate key from password
            key = base64.urlsafe_b64encode(password.ljust(32)[:32].encode('utf-8'))
            cipher = Fernet(key)

            # Encrypt the message
            encrypted_message = cipher.encrypt(message.encode('utf-8'))

            # Encode the encrypted message into the image
            output_path = file_path.rsplit('.', 1)[0] + '_encoded.png'
            lsb.hide(file_path, encrypted_message.decode('utf-8')).save(output_path)
            messagebox.showinfo("Success", f"Message encoded and saved to {output_path}")
            self.reset_entries()  # Clear entries after successful encoding
        except Exception as e:
            messagebox.showerror("Encoding Error", f"An error occurred: {str(e)}")

    def decode_message(self):
        file_path = self.file_entry.get().strip()
        password = self.password_entry.get().strip()
        if not file_path or not password:
            messagebox.showerror("Error", "Please select a file and provide a password.")
            return

        try:
            # Generate key from password
            key = base64.urlsafe_b64encode(password.ljust(32)[:32].encode('utf-8'))
            cipher = Fernet(key)

            # Decode the message from the image
            encrypted_message = lsb.reveal(file_path)

            # Decrypt the message
            decoded_message = cipher.decrypt(encrypted_message.encode('utf-8')).decode('utf-8')

            self.results_text.configure(state='normal')  # Enable text box to insert text
            self.results_text.delete('1.0', tk.END)
            self.results_text.insert(tk.END, decoded_message)
            self.results_text.configure(state='disabled')  # Set back to read-only
        except Exception as e:
            messagebox.showerror("Decoding Error", f"An error occurred: {str(e)}")

    def reset_entries(self):
        self.file_entry.configure(state='normal')  # Allow clearing file entry
        self.file_entry.delete(0, tk.END)
        self.file_entry.configure(state='readonly')  # Set back to read-only

        self.message_text.delete("1.0", tk.END)
        self.password_entry.delete(0, tk.END)
        self.image_label.configure(image=None, text="No image selected")

def generate_key(password):
    return base64.urlsafe_b64encode(password.ljust(32)[:32].encode('utf-8'))

def encode_image_cli(input_image, message, password):
    try:
        # Generate key and encrypt the message
        key = generate_key(password)
        cipher = Fernet(key)
        encrypted_message = cipher.encrypt(message.encode('utf-8'))

        # Encode the message into the image
        output_image = input_image.rsplit('.', 1)[0] + '_encoded.png'
        lsb.hide(input_image, encrypted_message.decode('utf-8')).save(output_image)
        print(f"Message successfully encoded and saved to {output_image}")
    except Exception as e:
        print(f"Error encoding the message: {str(e)}")

def decode_image_cli(input_image, password):
    try:
        # Generate key and decrypt the message
        key = generate_key(password)
        cipher = Fernet(key)
        encrypted_message = lsb.reveal(input_image)
        decoded_message = cipher.decrypt(encrypted_message.encode('utf-8')).decode('utf-8')
        print(f"Decoded Message: {decoded_message}")
    except Exception as e:
        print(f"Error decoding the message: {str(e)}")

def main():
    parser = argparse.ArgumentParser(
        description="Image Steganography Tool - Hide or reveal messages in images"
    )
    subparsers = parser.add_subparsers(dest='command')

    # Encode command
    encode_parser = subparsers.add_parser('encode', help='Encode a message into an image')
    encode_parser.add_argument('input_image', help='Path to the input image file (e.g., image.png)')
    encode_parser.add_argument('message', help='The message you want to encode')
    encode_parser.add_argument('password', help='Password to encrypt the message')

    # Decode command
    decode_parser = subparsers.add_parser('decode', help='Decode a hidden message from an image')
    decode_parser.add_argument('input_image', help='Path to the encoded image file (e.g., image_encoded.png)')
    decode_parser.add_argument('password', help='Password used for decryption')

    args = parser.parse_args()

    if args.command == 'encode':
        encode_image_cli(args.input_image, args.message, args.password)
    elif args.command == 'decode':
        decode_image_cli(args.input_image, args.password)
    else:
        # If no arguments are provided, start the GUI
        root = ctk.CTk()
        app = SteganographyGUI(root)
        root.mainloop()

if __name__ == "__main__":
    main()
