import customtkinter as ctk
from PIL import Image
from customtkinter import CTkImage
from ui.base_window import BaseMainApp
from ui.converter_window import ConverterWindow
from ui.theme import apply_theme, Colors, Fonts, get_button_style
from utils.system_utils import is_ffmpeg_installed
import os
from tkinter import messagebox


class Main(BaseMainApp):
    def __init__(self):
        # Inherit from BaseMainApp
        super().__init__(title="Oneverter", geometry="1280x720")
        
        # Apply the new modern theme
        apply_theme()
        self.configure(fg_color=Colors.BACKGROUND)

        # Make the window resizable
        self.resizable(True, True)
        
        # Set min size for responsiveness
        self.minsize(800, 600)

        if not is_ffmpeg_installed():
            messagebox.showwarning("ffmpeg Not Found", "ffmpeg is not installed or not in your system's PATH. Some audio and video conversion features may not work correctly.")

        self.setup_ui()

    def setup_ui(self):
        # Configure grid layout to be responsive
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Main content frame
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.grid(row=0, column=0, sticky="nsew", padx=40, pady=40)

        main_frame.grid_rowconfigure((0, 4), weight=1) 
        main_frame.grid_columnconfigure(0, weight=1)

        # Logo
        try:
            logo_image_path = "assets/main_logo.png"
            if os.path.exists(logo_image_path):
                logo_image = Image.open(logo_image_path).resize((200, 200))
                logo_photo = CTkImage(light_image=logo_image, size=(200, 200))
                logo_label = ctk.CTkLabel(main_frame, image=logo_photo, text="", bg_color="transparent")
                logo_label.grid(row=0, column=0, pady=(20, 10), sticky="s")
        except Exception as e:
            print(f"Failed to load logo: {e}")
            ctk.CTkLabel(main_frame, text="🚀", font=ctk.CTkFont(size=120)).grid(row=0, column=0, pady=(20, 10), sticky="s")

        # Title
        ctk.CTkLabel(
            main_frame, text="Oneverter", font=Fonts.TITLE, text_color=Colors.TEXT
        ).grid(row=1, column=0, pady=(10, 5))

        # Subtitle
        ctk.CTkLabel(
            main_frame, text="Your All-in-One Conversion Hub", font=Fonts.SUBTITLE, text_color=Colors.SUBTLE_TEXT
        ).grid(row=2, column=0, pady=(0, 30))

        # Start Button
        ctk.CTkButton(
            main_frame, 
            text="🚀 Start Conversion", 
            command=self.start_conversion,
            **get_button_style()
        ).grid(row=3, column=0, pady=20, ipady=10)
        
        # Theme toggle (removed for a consistent dark theme)
        
        # Footer
        ctk.CTkLabel(
            main_frame, text="© 2025 QPPD • Oneverter", font=Fonts.SMALL, text_color=Colors.SUBTLE_TEXT
        ).grid(row=4, column=0, pady=(20, 10), sticky="s")

    def start_conversion(self):
        print("Launching conversion UI...")
        self.open_toplevel_window(ConverterWindow)


if __name__ == "__main__":
    app = Main()
    app.mainloop()
