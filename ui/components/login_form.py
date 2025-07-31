import customtkinter as ctk
from tkinter import messagebox
from ui.theme import Colors, get_label_style, get_button_style

class LoginForm(ctk.CTkFrame):
    def __init__(self, parent, on_submit, on_toggle, on_oauth_google, on_oauth_github):
        super().__init__(parent, fg_color="transparent")
        self.on_submit = on_submit
        self.on_toggle = on_toggle
        self.on_oauth_google = on_oauth_google
        self.on_oauth_github = on_oauth_github
        self.is_login_mode = True
        self.setup_form()

    def setup_form(self):
        self.grid_columnconfigure(0, weight=1)
        self.title_label = ctk.CTkLabel(self, text="Oneverter", **get_label_style("title"))
        self.title_label.pack(pady=(0, 30))
        self.email_entry = ctk.CTkEntry(self, placeholder_text="Email", width=400, height=45)
        self.email_entry.pack(pady=(0, 15))
        self.password_entry = ctk.CTkEntry(self, placeholder_text="Password", show="*", width=400, height=45)
        self.password_entry.pack(pady=(0, 15))
        self.confirm_password_entry = ctk.CTkEntry(self, placeholder_text="Confirm Password", show="*", width=400, height=45)
        self.error_label = ctk.CTkLabel(self, text="", text_color=Colors.ACCENT)
        self.error_label.pack(pady=(0, 15))
        self.remember_me_checkbox = ctk.CTkCheckBox(self, text="Remember Me", text_color=Colors.SUBTLE_TEXT)
        self.remember_me_checkbox.pack(pady=(0, 20))
        self.submit_button = ctk.CTkButton(self, text="Login", **get_button_style(), width=400, height=45, command=self.handle_submit)
        self.submit_button.pack(pady=(0, 15))
        self.toggle_link = ctk.CTkLabel(self, text="Don't have an account? Sign Up", cursor="hand2", text_color=Colors.BUTTON)
        self.toggle_link.bind("<Button-1>", self.handle_toggle)
        self.toggle_link.pack(pady=(0, 25))
        separator = ctk.CTkLabel(self, text="────────────  OR  ────────────", text_color=Colors.SUBTLE_TEXT)
        separator.pack(pady=(0, 20))
        self.google_button = ctk.CTkButton(self, text="Continue with Google", **get_button_style(), width=400, height=45, command=self.on_oauth_google)
        self.google_button.pack(pady=(0, 10))
        self.github_button = ctk.CTkButton(self, text="Continue with GitHub", **get_button_style(), width=400, height=45, command=self.on_oauth_github)
        self.github_button.pack(pady=(0, 0))
        self.show_login_form()

    def show_login_form(self):
        self.title_label.configure(text="Login")
        self.submit_button.configure(text="Login")
        self.toggle_link.configure(text="Don't have an account? Sign Up")
        self.confirm_password_entry.pack_forget()
        self.remember_me_checkbox.pack(pady=(0, 20))
        self.is_login_mode = True
        self.error_label.configure(text="")

    def show_signup_form(self):
        self.title_label.configure(text="Sign Up")
        self.submit_button.configure(text="Sign Up")
        self.toggle_link.configure(text="Already have an account? Login")
        self.remember_me_checkbox.pack_forget()
        self.confirm_password_entry.pack(pady=(0, 15), after=self.password_entry)
        self.is_login_mode = False
        self.error_label.configure(text="")

    def handle_toggle(self, event=None):
        if self.is_login_mode:
            self.show_signup_form()
        else:
            self.show_login_form()
        if self.on_toggle:
            self.on_toggle(self.is_login_mode)

    def handle_submit(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get() if not self.is_login_mode else None
        remember_me = self.remember_me_checkbox.get()
        if self.on_submit:
            # Firebase integration
            from utils.firebase_auth_provider import FirebaseAuthProvider
            firebase_auth = FirebaseAuthProvider()
            if self.is_login_mode:
                success, result = firebase_auth.login(email, password)
                if success:
                    # MFA: Check email verification
                    id_token = result.get('idToken') if isinstance(result, dict) else None
                    if id_token and not firebase_auth.is_email_verified(id_token):
                        messagebox.showwarning("Email Not Verified", "Please verify your email address before logging in. Check your inbox for a verification link.")
                    else:
                        messagebox.showinfo("Login Success", f"Welcome!")
                else:
                    messagebox.showerror("Login Failed", result)
            else:
                if password != confirm_password:
                    messagebox.showerror("Signup Failed", "Passwords do not match.")
                    return
                success, result = firebase_auth.signup(email, password)
                if success:
                    messagebox.showinfo("Signup Success", "Account created! Please check your email for a verification link.")
                else:
                    messagebox.showerror("Signup Failed", result)

    def set_error(self, message):
        self.error_label.configure(text=message)

    def set_default_credentials(self, email, password):
        self.email_entry.delete(0, 'end')
        self.email_entry.insert(0, email)
        self.password_entry.delete(0, 'end')
        self.password_entry.insert(0, password)
