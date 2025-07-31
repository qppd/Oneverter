import customtkinter as ctk
from tkinter import filedialog, messagebox
from ui.theme import Colors, get_label_style, get_button_style
from utils.firebase_auth_provider import FirebaseAuthProvider

class ProfileForm(ctk.CTkFrame):
    def __init__(self, parent, id_token, user_id):
        super().__init__(parent, fg_color="transparent")
        self.id_token = id_token
        self.user_id = user_id
        self.firebase_auth = FirebaseAuthProvider()
        self.setup_form()

    def setup_form(self):
        self.grid_columnconfigure(0, weight=1)
        self.title_label = ctk.CTkLabel(self, text="Edit Profile", **get_label_style("title"))
        self.title_label.pack(pady=(0, 30))
        self.display_name_entry = ctk.CTkEntry(self, placeholder_text="Display Name", width=400, height=45)
        self.display_name_entry.pack(pady=(0, 15))
        self.avatar_button = ctk.CTkButton(self, text="Upload Avatar", **get_button_style(), width=400, height=45, command=self.handle_avatar_upload)
        self.avatar_button.pack(pady=(0, 15))
        self.save_button = ctk.CTkButton(self, text="Save Changes", **get_button_style(), width=400, height=45, command=self.handle_save)
        self.save_button.pack(pady=(0, 15))
        self.status_label = ctk.CTkLabel(self, text="", text_color=Colors.ACCENT)
        self.status_label.pack(pady=(0, 15))

    def handle_avatar_upload(self):
        file_path = filedialog.askopenfilename(title="Select Avatar", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            success, photo_url = self.firebase_auth.upload_avatar(file_path, self.user_id)
            if success:
                self.status_label.configure(text="Avatar uploaded!")
                self.photo_url = photo_url
            else:
                messagebox.showerror("Upload Failed", photo_url)

    def handle_save(self):
        display_name = self.display_name_entry.get()
        photo_url = getattr(self, 'photo_url', None)
        success, result = self.firebase_auth.update_profile(self.id_token, display_name, photo_url)
        if success:
            messagebox.showinfo("Profile Updated", "Your profile has been updated.")
        else:
            messagebox.showerror("Update Failed", result)
