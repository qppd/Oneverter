import customtkinter as ctk
from ui.unified_main_window import UnifiedMainWindow
from ui.theme import apply_theme
from utils.system_utils import is_ffmpeg_installed
from tkinter import messagebox


class App:
    def __init__(self):
        # Main window
        self.root = ctk.CTk()
        
        # Apply theme
        apply_theme()
        
        # Configure window
        self.root.title("Oneverter - File Converter")
        # Make window maximized for full screen usage with responsive content
        self.root.state("zoomed")  # Maximized window
        self.root.minsize(1000, 700)  # Minimum size for responsiveness
        
        # Show main app directly
        self.show_main_app()

    def show_main_app(self):
        # Use the unified main window
        self.main_app = UnifiedMainWindow(
            master=self.root,
            user_manager=None,
            logout_callback=None
        )
        self.main_app.pack(expand=True, fill="both")

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
