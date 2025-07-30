import customtkinter as ctk
from PIL import Image
from customtkinter import CTkImage
from ui.base_window import BaseMainApp
from ui.converter_window import ConverterWindow
import os


class Main(BaseMainApp):
    def __init__(self):
        # Inherit from BaseMainApp
        super().__init__(title="Oneverter", geometry="1280x720")
        
        # Make the window resizable
        self.resizable(True, True)
        
        # Set min size for responsiveness
        self.minsize(800, 600)

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.setup_ui()

    def setup_ui(self):
        # Configure grid layout to be responsive
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Background Frame
        bg_frame = ctk.CTkFrame(self, corner_radius=0)
        bg_frame.grid(row=0, column=0, sticky="nsew")
        bg_frame.grid_rowconfigure(0, weight=1)
        bg_frame.grid_columnconfigure(0, weight=1)

        # Background Image
        try:
            # Note: A fixed-size background image won't scale well in a responsive layout.
            # It's better to use a solid color or a tiling pattern.
            bg_image_path = "assets/main_bg.png"
            if os.path.exists(bg_image_path):
                bg_image = Image.open(bg_image_path)
                bg_photo = CTkImage(light_image=bg_image, size=bg_image.size)
                bg_label = ctk.CTkLabel(bg_frame, image=bg_photo, text="")
                bg_label.place(relx=0.5, rely=0.5, anchor="center") # place is okay for bg
        except Exception as e:
            print(f"Failed to load background image: {e}")
            bg_frame.configure(fg_color=("#2b2b2b", "#1a1a1a"))

        # Overlay Frame for content
        overlay = ctk.CTkFrame(bg_frame, fg_color="transparent")
        overlay.grid(row=0, column=0, sticky="nsew")

        # Configure overlay grid to center content
        overlay.grid_rowconfigure((0, 4), weight=1) # Push content to center
        overlay.grid_columnconfigure(0, weight=1)

        # Logo
        try:
            logo_image_path = "assets/main_logo.png"
            if os.path.exists(logo_image_path):
                logo_image = Image.open(logo_image_path).resize((200, 200))
                logo_photo = CTkImage(light_image=logo_image, size=(200, 200))
                logo_label = ctk.CTkLabel(overlay, image=logo_photo, text="", bg_color="transparent")
                logo_label.grid(row=0, column=0, pady=(20, 10), sticky="s")
        except Exception as e:
            print(f"Failed to load logo: {e}")
            ctk.CTkLabel(overlay, text="🚀", font=ctk.CTkFont(size=72)).grid(row=0, column=0, pady=(20, 10), sticky="s")

        # Title
        ctk.CTkLabel(
            overlay, text="Oneverter", font=ctk.CTkFont(size=32, weight="bold")
        ).grid(row=1, column=0, pady=10)

        # Subtitle
        ctk.CTkLabel(
            overlay, text="Your All-in-One Conversion Hub", font=ctk.CTkFont(size=16)
        ).grid(row=2, column=0, pady=5)

        # Start Button
        ctk.CTkButton(
            overlay, text="🚀 Start Conversion", 
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self.start_conversion
        ).grid(row=3, column=0, pady=20)
        
        # Footer
        ctk.CTkLabel(
            overlay, text="© 2025 QPPD • Oneverter", font=ctk.CTkFont(size=12)
        ).grid(row=4, column=0, pady=10, sticky="s")

    def start_conversion(self):
        print("Launching conversion UI...")
        # Use the inherited method to open the next window
        self.open_toplevel_window(ConverterWindow)


if __name__ == "__main__":
    app = Main()
    app.mainloop()
