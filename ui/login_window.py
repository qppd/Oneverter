import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
from .base_window import BaseWindow
from ui.theme import Colors, Fonts, get_button_style, get_frame_style, get_label_style
from utils.user_manager import UserManager
from utils.oauth_flow_manager import OAuthFlowManager


class LoginWindow(BaseWindow):
    def __init__(self, parent, user_manager: UserManager, on_success: callable):
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
        self.configure(fg_color=Colors.BACKGROUND)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        wrapper_frame = ctk.CTkFrame(self, fg_color="transparent")
        wrapper_frame.grid(row=0, column=0, sticky="nsew")
        wrapper_frame.grid_rowconfigure(0, weight=1)
        wrapper_frame.grid_columnconfigure(0, weight=1)

        # Center Frame - like a card
        center_frame = ctk.CTkFrame(wrapper_frame, **get_frame_style())
        center_frame.grid(row=0, column=0, sticky="n", pady=60, padx=30)
        center_frame.grid_columnconfigure(0, weight=1)

        # Inner content with padding
        content_wrapper = ctk.CTkFrame(center_frame, fg_color="transparent")
        content_wrapper.pack(padx=40, pady=40, fill="both", expand=True)

        # Title
        self.title_label = ctk.CTkLabel(content_wrapper, text="Oneverter", **get_label_style("title"))
        self.title_label.pack(pady=(0, 30))

        # --- Input Fields ---
        self.email_entry = ctk.CTkEntry(content_wrapper, placeholder_text="Email", width=400, height=45)
        self.email_entry.pack(pady=(0, 15))

        self.password_entry = ctk.CTkEntry(content_wrapper, placeholder_text="Password", show="*", width=400, height=45)
        self.password_entry.pack(pady=(0, 15))

        self.confirm_password_entry = ctk.CTkEntry(content_wrapper, placeholder_text="Confirm Password", show="*", width=400, height=45)

        # --- Error Label ---
        self.error_label = ctk.CTkLabel(content_wrapper, text="", text_color=Colors.ACCENT)
        self.error_label.pack(pady=(0, 15))

        # --- Remember Me ---
        self.remember_me_checkbox = ctk.CTkCheckBox(content_wrapper, text="Remember Me", text_color=Colors.SUBTLE_TEXT)
        self.remember_me_checkbox.pack(pady=(0, 20))

        # --- Submit Button ---
        self.submit_button = ctk.CTkButton(content_wrapper, text="Login", **get_button_style(), width=400, height=45, command=self.handle_submit)
        self.submit_button.pack(pady=(0, 15))

        # --- Toggle Link ---
        self.toggle_link = ctk.CTkLabel(content_wrapper, text="Don't have an account? Sign Up", cursor="hand2", text_color=Colors.BUTTON)
        self.toggle_link.bind("<Button-1>", self.toggle_form)
        self.toggle_link.pack(pady=(0, 25))

        # --- OR Separator ---
        separator = ctk.CTkLabel(content_wrapper, text="────────────  OR  ────────────", text_color=Colors.SUBTLE_TEXT)
        separator.pack(pady=(0, 20))

        # --- OAuth Buttons ---
        self.google_button = ctk.CTkButton(content_wrapper, text="Continue with Google", **get_button_style(), width=400, height=45, command=self.handle_google_login)
        self.google_button.pack(pady=(0, 10))

        self.github_button = ctk.CTkButton(content_wrapper, text="Continue with GitHub", **get_button_style(), width=400, height=45, command=self.handle_github_login)
        self.github_button.pack(pady=(0, 0))

    def show_login_form(self):
        self.title_label.configure(text="Login")
        self.submit_button.configure(text="Login")
        self.toggle_link.configure(text="Don't have an account? Sign Up")
        self.confirm_password_entry.pack_forget()
        self.remember_me_checkbox.pack(pady=(5, 10))
        self.is_login_mode = True
        self.error_label.configure(text="")

    def show_signup_form(self):
        self.title_label.configure(text="Sign Up")
        self.submit_button.configure(text="Sign Up")
        self.toggle_link.configure(text="Already have an account? Login")
        self.confirm_password_entry.pack(pady=(5, 10))
        self.remember_me_checkbox.pack_forget()
        self.is_login_mode = False
        self.error_label.configure(text="")

    def toggle_form(self, event=None):
        if self.is_login_mode:
            self.show_signup_form()
        else:
            self.show_login_form()

    def handle_submit(self):
        email = self.email_entry.get()
        password = self.password_entry.get()

        if self.is_login_mode:
            success, message = self.user_manager.login(email, password)
            if success:
                if self.remember_me_checkbox.get():
                    self.user_manager.save_session(email)
                else:
                    self.user_manager.clear_session()
                self.on_success()
            else:
                self.error_label.configure(text=message)
        else:
            confirm_password = self.confirm_password_entry.get()
            if password != confirm_password:
                self.error_label.configure(text="Passwords do not match.")
                return

            success, message = self.user_manager.signup(email, password)
            if success:
                messagebox.showinfo("Success", message)
                self.show_login_form()
            else:
                self.error_label.configure(text=message)

    def handle_oauth_success(self, user_info):
        success, message = self.user_manager.oauth_login(user_info)
        if success:
            self.after(0, self.on_success)
        else:
            self.after(0, lambda: self.error_label.configure(text=message))

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
