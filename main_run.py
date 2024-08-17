import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

# Import the video and image steganography GUIs
from video_gui import VideoSteganographyGUI
from image_gui_cli import SteganographyGUI

class SteganographyLauncher(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Steganography Tool Launcher")

        # Set the window size
        window_width = 600
        window_height = 200

        # Calculate the center position
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int((screen_width / 1.43) - (window_width / 1.5))
        center_y = int((screen_height / 1.5) - (window_height / 1.5))

        # Set the geometry to center the window
        self.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        self.configure(bg='#2E2E2E')  # Set background color for the main window

        # Set theme colors
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.create_widgets()

    def create_widgets(self):
        # Create and place the header
        header = ctk.CTkLabel(self, text="Steganography Tool Launcher", font=("Arial", 20, "bold"))
        header.pack(pady=20)

        # Create buttons to launch the respective tools
        video_button = ctk.CTkButton(self, text="Video Steganography", command=self.launch_video_steganography)
        video_button.pack(pady=10, padx=20, fill="both")

        image_button = ctk.CTkButton(self, text="Image Steganography", command=self.launch_image_steganography)
        image_button.pack(pady=10, padx=20, fill="both")

    def launch_video_steganography(self):
        # Schedule the video GUI to open in the main thread
        self.after(0, self.open_video_window)

    def launch_image_steganography(self):
        # Schedule the image GUI to open in the main thread
        self.after(0, self.open_image_window)

    def open_video_window(self):
        video_app = VideoSteganographyGUI()
        video_app.mainloop()

    def open_image_window(self):
        root = ctk.CTk()
        image_app = SteganographyGUI(root)
        root.mainloop()

if __name__ == "__main__":
    app = SteganographyLauncher()
    app.mainloop()
