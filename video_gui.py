import customtkinter as ctk
from tkinter import filedialog, messagebox
import cv2
from video import encrypt_message, decrypt_message, hide_data_in_video, unhide_data_from_video

class VideoSteganographyGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Video Steganography Tool")

        # Set the window size
        window_width = 700
        window_height = 530

        # Calculate the center position
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int((screen_width / 1.43) - (window_width / 1.5))
        center_y = int((screen_height / 1.7) - (window_height / 1.5))

        # Set the geometry to center the window
        self.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        self.configure(bg='#2E2E2E')  # Set background color for the main window
        
        # Set theme colors
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.create_widgets()

    def create_widgets(self):
        # Create and place the header
        header = ctk.CTkLabel(self, text="Video Steganography Tool", font=("Arial", 20, "bold"))
        header.pack(pady=20)

        # Create and place the tabs
        tabview = ctk.CTkTabview(self)
        tabview.pack(padx=20, pady=10, fill="both", expand=True)
        
        # Add tabs
        hide_tab = tabview.add("Hide Data")
        unhide_tab = tabview.add("Unhide Data")
        
        # Hide Data Tab Widgets
        self.create_hide_tab_widgets(hide_tab)
        
        # Unhide Data Tab Widgets
        self.create_unhide_tab_widgets(unhide_tab)
        
    def create_hide_tab_widgets(self, parent):
        ctk.CTkLabel(parent, text="Input Video File:", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.input_video_path = ctk.CTkEntry(parent, width=300)
        self.input_video_path.grid(row=0, column=1, padx=10, pady=10)
        ctk.CTkButton(parent, text="Browse", command=self.browse_input_video).grid(row=0, column=2, padx=10, pady=10)
        
        ctk.CTkLabel(parent, text="Output Video File:", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.output_video_path = ctk.CTkEntry(parent, width=300)
        self.output_video_path.grid(row=1, column=1, padx=10, pady=10)
        ctk.CTkButton(parent, text="Browse", command=self.browse_output_video).grid(row=1, column=2, padx=10, pady=10)
        
        ctk.CTkLabel(parent, text="Message:", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.message = ctk.CTkTextbox(parent, width=300, height=100)
        self.message.grid(row=2, column=1, padx=10, pady=10)
        
        ctk.CTkLabel(parent, text="Password:", font=("Arial", 12)).grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.password_entry = ctk.CTkEntry(parent, show="*", width=300)
        self.password_entry.grid(row=3, column=1, padx=10, pady=10)
        
        ctk.CTkLabel(parent, text="Codec:", font=("Arial", 12)).grid(row=4, column=0, padx=10, pady=10, sticky="w")
        self.codec_var = ctk.StringVar(value='FFV1')
        codec_options = ['HFYU', 'FFV1']
        self.codec_menu = ctk.CTkOptionMenu(parent, variable=self.codec_var, values=codec_options)
        self.codec_menu.grid(row=4, column=1, padx=10, pady=10)

        ctk.CTkButton(parent, text="Hide Data", command=self.hide_data).grid(row=5, column=0, columnspan=3, padx=10, pady=20)
        
    def create_unhide_tab_widgets(self, parent):
        ctk.CTkLabel(parent, text="Input Video File:", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.unhide_input_video_path = ctk.CTkEntry(parent, width=300)
        self.unhide_input_video_path.grid(row=0, column=1, padx=10, pady=10)
        ctk.CTkButton(parent, text="Browse", command=self.browse_unhide_input_video).grid(row=0, column=2, padx=10, pady=10)
        
        ctk.CTkLabel(parent, text="Password:", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.unhide_password_entry = ctk.CTkEntry(parent, show="*", width=300)
        self.unhide_password_entry.grid(row=1, column=1, padx=10, pady=10)
        
        self.unhide_message_textbox = ctk.CTkTextbox(parent, width=300, height=100)
        self.unhide_message_textbox.grid(row=2, column=0, columnspan=3, padx=10, pady=20)
        
        ctk.CTkButton(parent, text="Unhide Data", command=self.unhide_data).grid(row=3, column=0, columnspan=3, padx=10, pady=20)
        
    def browse_input_video(self):
        file_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.avi *.mov")])
        if file_path:
            self.input_video_path.delete(0, ctk.END)
            self.input_video_path.insert(0, file_path)
    
    def browse_output_video(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".avi", filetypes=[("AVI Files", "*.avi"), ("MP4 Files", "*.mp4")])
        if file_path:
            self.output_video_path.delete(0, ctk.END)
            self.output_video_path.insert(0, file_path)
    
    def browse_unhide_input_video(self):
        file_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.avi *.mov")])
        if file_path:
            self.unhide_input_video_path.delete(0, ctk.END)
            self.unhide_input_video_path.insert(0, file_path)

    def hide_data(self):
        input_path = self.input_video_path.get()
        output_path = self.output_video_path.get()
        message = self.message.get("1.0", ctk.END).strip()
        password = self.password_entry.get()
        codec = self.codec_var.get()

        if not input_path or not output_path or not message or not password:
            messagebox.showerror("Input Error", "Please fill in all fields.")
            return

        try:
            encrypted_message = encrypt_message(message, password)
            frame_rate, frame_width, frame_height = self.get_video_properties(input_path)
            codec_dict = {'HFYU': cv2.VideoWriter_fourcc(*'HFYU'), 'FFV1': cv2.VideoWriter_fourcc(*'FFV1')}
            codec = codec_dict.get(codec, cv2.VideoWriter_fourcc(*'XVID'))
            hide_data_in_video(input_path, output_path, frame_rate, frame_width, frame_height, codec, message, password)
            messagebox.showinfo("Success", "Data hidden in video successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Error hiding data: {e}")


    def unhide_data(self):
        video_path = self.unhide_input_video_path.get()
        password = self.unhide_password_entry.get()

        if not video_path or not password:
            messagebox.showerror("Input Error", "Please fill in all fields.")
            return

        try:
            decrypted_message = unhide_data_from_video(video_path, password)
            if decrypted_message:
                self.unhide_message_textbox.delete("1.0", ctk.END)
                self.unhide_message_textbox.insert("1.0", decrypted_message)
            else:
                messagebox.showerror("Error", "Failed to unhide data or incorrect password.")
        except Exception as e:
            messagebox.showerror("Error", f"Error unhiding data: {e}")


    def get_video_properties(self, video_path):
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise Exception(f"Error opening video file {video_path}.")
        frame_rate = cap.get(cv2.CAP_PROP_FPS)
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()
        return frame_rate, frame_width, frame_height

if __name__ == "__main__":
    app = VideoSteganographyGUI()
    app.mainloop()