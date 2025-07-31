import customtkinter as ctk
from PIL import Image
from customtkinter import CTkImage
from ui.unified_main_window import UnifiedMainWindow
from ui.theme import apply_theme, Colors, Fonts, get_button_style
from utils.system_utils import is_ffmpeg_installed
import os
from tkinter import messagebox
from ui.login_window import LoginWindow
from utils.secure_user_manager import SecureUserManager
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class App:
    def __init__(self):
        self.user_manager = SecureUserManager()

        # Main window is created but not displayed yet
        self.root = ctk.CTk()
        self.root.withdraw() # Hide root window initially
        
        # Apply theme
        apply_theme()

        self.show_login_or_main()

    def show_login_or_main(self):
        # Try to restore session from stored data
        if self.user_manager.login_with_session():
            self.show_main_app()
        else:
            self.show_login_window()

    def show_login_window(self):
        self.login_window = LoginWindow(
            parent=self.root,
            user_manager=self.user_manager,
            on_success=self.show_main_app
        )
    
    def show_main_app(self):
        # Destroy login window if it exists
        if hasattr(self, 'login_window') and self.login_window.winfo_exists():
            self.login_window.destroy()
        
        # Instead of creating a new root, we deiconify and setup the main app
        self.root.deiconify()
        
        # Use the new unified main window
        self.main_app = UnifiedMainWindow(
            master=self.root,
            user_manager=self.user_manager,
            logout_callback=self.handle_logout
        )
        self.main_app.pack(expand=True, fill="both")

    def handle_logout(self):
        self.user_manager.logout()
        self.root.withdraw()  # Hide the main window
        if hasattr(self, 'main_app'):
            self.main_app.destroy()
        self.show_login_window()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    if not is_ffmpeg_installed():
        # This is a bit of a hack. Since root isn't created yet, we make a temporary one.
        root = ctk.CTk()
        root.withdraw()
        messagebox.showwarning("ffmpeg Not Found", "ffmpeg is not installed or not in your system's PATH. Some audio and video conversion features may not work correctly.")
        root.destroy()
        
    app = App()
    app.run()
