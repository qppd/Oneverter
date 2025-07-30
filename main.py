import customtkinter as ctk
from PIL import Image
from customtkinter import CTkImage
from ui.base_window import BaseMainApp
from ui.converter_window import ConverterWindow
from ui.theme import apply_theme, Colors, Fonts, get_button_style
from utils.system_utils import is_ffmpeg_installed
import os
from tkinter import messagebox
from ui.login_window import LoginWindow
from utils.user_manager import UserManager
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Main(ctk.CTkFrame):
    def __init__(self, master, user_manager: UserManager, logout_callback: callable):
        super().__init__(master)
        self.user_manager = user_manager
        self.logout_callback = logout_callback

        # Apply the new modern theme
        apply_theme()
        self.configure(fg_color=Colors.BACKGROUND)

        # Make the window resizable
        if isinstance(master, ctk.CTk):
            master.resizable(True, True)
            # Set min size for responsiveness
            master.minsize(800, 600)
            master.title("Oneverter")

        self.setup_ui()

    def setup_ui(self):
        # Top bar for user info and logout
        top_bar = ctk.CTkFrame(self, fg_color=Colors.FRAME, height=50)
        top_bar.pack(side="top", fill="x", padx=10, pady=(10,0))
        
        user = self.user_manager.get_current_user()
        welcome_text = f"Welcome, {user['name']}!" if user else "Welcome!"
        
        welcome_label = ctk.CTkLabel(top_bar, text=welcome_text, font=Fonts.BODY, text_color=Colors.TEXT)
        welcome_label.pack(side="left", padx=20)
        
        logout_button = ctk.CTkButton(top_bar, text="Logout", **get_button_style("danger"), width=100, command=self.logout_callback)
        logout_button.pack(side="right", padx=20)

        # Configure grid layout to be responsive
        self.pack_propagate(False) # Prevent top_bar from shrinking the container
        
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(expand=True, fill="both", padx=10, pady=10)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        # Central frame for the main content
        center_frame = ctk.CTkFrame(container, fg_color="transparent")
        center_frame.grid(row=0, column=0)

        # Logo
        try:
            logo_image_path = "assets/main_logo.png"
            if os.path.exists(logo_image_path):
                logo_image = Image.open(logo_image_path).resize((200, 200))
                logo_photo = CTkImage(light_image=logo_image, size=(200, 200))
                logo_label = ctk.CTkLabel(center_frame, image=logo_photo, text="", bg_color="transparent")
                logo_label.grid(row=0, column=0, pady=(20, 10), sticky="s")
        except Exception as e:
            print(f"Failed to load logo: {e}")
            ctk.CTkLabel(center_frame, text="🚀", font=ctk.CTkFont(size=120)).grid(row=0, column=0, pady=(20, 10), sticky="s")

        # Title
        ctk.CTkLabel(
            center_frame, text="Oneverter", font=Fonts.TITLE, text_color=Colors.TEXT
        ).grid(row=1, column=0, pady=(10, 5))

        # Subtitle
        ctk.CTkLabel(
            center_frame, text="Your All-in-One Conversion Hub", font=Fonts.SUBTITLE, text_color=Colors.SUBTLE_TEXT
        ).grid(row=2, column=0, pady=(0, 30))

        # Start Button
        ctk.CTkButton(
            center_frame, 
            text="🚀 Start Conversion", 
            command=self.start_conversion,
            **get_button_style()
        ).grid(row=3, column=0, pady=20, ipady=10)
        
        # Theme toggle (removed for a consistent dark theme)
        
        # Footer
        ctk.CTkLabel(
            center_frame, text="© 2025 QPPD • Oneverter", font=Fonts.SMALL, text_color=Colors.SUBTLE_TEXT
        ).grid(row=4, column=0, pady=(20, 10), sticky="s")

    def start_conversion(self):
        print("Launching conversion UI...")
        # The following line is removed because the parent of this frame is now the main app,
        # not a window that can open other windows.
        # self.open_toplevel_window(ConverterWindow)
        
        # Instead, we can create and manage the window from here,
        # but it needs a reference to the root app or handle windowing differently.
        # For now, let's just create the window.
        if not hasattr(self, 'converter_window') or not self.converter_window.winfo_exists():
            self.converter_window = ConverterWindow(self.master)
            self.converter_window.grab_set()
        else:
            self.converter_window.deiconify()
            self.converter_window.grab_set()


class App:
    def __init__(self):
        self.user_manager = UserManager()

        # Main window is created but not displayed yet
        self.root = ctk.CTk()
        self.root.withdraw() # Hide root window initially
        
        # Apply theme
        apply_theme()

        self.show_login_or_main()

    def show_login_or_main(self):
        # For now, we always show the login window.
        # Later, we can add session management to bypass this.
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
        
        # Pass the root to Main app
        self.main_app = Main(
            master=self.root, 
            user_manager=self.user_manager,
            logout_callback=self.handle_logout
        )
        self.main_app.pack(expand=True, fill="both")

    def handle_logout(self):
        self.user_manager.logout()
        self.user_manager.clear_session()
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
