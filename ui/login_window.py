import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
from .base_window import BaseWindow
from ui.theme import Colors, Fonts, get_button_style, get_frame_style, get_label_style
from utils.secure_user_manager import SecureUserManager
from utils.oauth_flow_manager import OAuthFlowManager


class LoginWindow(BaseWindow):
    def __init__(self, parent, user_manager: SecureUserManager, on_success: callable):
        super().__init__(parent, title="Login - Oneverter", geometry="1280x720")
        self.user_manager = user_manager
        self.on_success = on_success

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.resizable(True, True)
        self.minsize(900, 700)

        self.grab_set()
        self.transient(parent)

        self.setup_ui()
        self.show_login_form()

    def on_close(self):
        self.parent.destroy()

    def setup_ui(self):
        from ui.components.login_form import LoginForm
        self.configure(fg_color=Colors.BACKGROUND)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        wrapper_frame = ctk.CTkFrame(self, fg_color="transparent")
        wrapper_frame.grid(row=0, column=0, sticky="nsew")
        wrapper_frame.grid_rowconfigure(0, weight=1)
        wrapper_frame.grid_columnconfigure(0, weight=1)

        center_frame = ctk.CTkFrame(wrapper_frame, **get_frame_style())
        center_frame.grid(row=0, column=0, sticky="n", pady=60, padx=30)
        center_frame.grid_columnconfigure(0, weight=1)

        self.login_form = LoginForm(
            center_frame,
            on_submit=self.handle_submit,
            on_toggle=self.toggle_form,
            on_oauth_google=self.handle_google_login,
            on_oauth_github=self.handle_github_login
        )
        self.login_form.pack(padx=40, pady=40, fill="both", expand=True)

    def show_login_form(self):
        self.login_form.show_login_form()
        self.login_form.set_default_credentials('test@test.com', 'test123')

    def show_signup_form(self):
        self.login_form.show_signup_form()

    def toggle_form(self, is_login_mode=None):
        # is_login_mode is passed from LoginForm
        if is_login_mode is None:
            is_login_mode = self.login_form.is_login_mode
        if is_login_mode:
            self.show_login_form()
        else:
            self.show_signup_form()

    def handle_submit(self, email, password, confirm_password, remember_me, is_login_mode):
        # Debug account for easy testing
        if is_login_mode and email == "test@test.com" and password == "test123":
            self.on_success()
            return

        if is_login_mode:
            success, message, tokens = self.user_manager.login(
                email, password, remember_me=remember_me
            )
            if success:
                if tokens:
                    pass
                self.on_success()
            else:
                self.login_form.set_error(message)
        else:
            if password != confirm_password:
                self.login_form.set_error("Passwords do not match.")
                return
            success, message = self.user_manager.signup(email, password)
            if success:
                messagebox.showinfo("Success", message)
                self.show_login_form()
            else:
                self.login_form.set_error(message)

    def handle_oauth_success(self, user_info):
        success, message = self.user_manager.oauth_login(user_info)
        if success:
            self.after(0, self.on_success)
        else:
            self.after(0, lambda: self.login_form.set_error(message))

    def handle_google_login(self):
        self.error_label.configure(text="Waiting for Google authentication...")
        self.oauth_flow = OAuthFlowManager(
            provider_name='google',
            on_success=self.handle_oauth_success
        )
        self.oauth_flow.start_flow()

    def handle_github_login(self):
        self.error_label.configure(text="Waiting for GitHub authentication...")
        self.oauth_flow = OAuthFlowManager(
            provider_name='github',
            on_success=self.handle_oauth_success
        )
        self.oauth_flow.start_flow()
