import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
from mutagen.mp4 import MP4, MP4Cover

class MetadataEditorUI:
    def __init__(self, parent):
        self.parent = parent
        self.video_path = None
        self.setup_ui()

    def setup_ui(self):
        main_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # File Selection
        ctk.CTkButton(main_frame, text="Select Video File", command=self.load_video).pack(pady=10)
        self.file_label = ctk.CTkLabel(main_frame, text="No video selected")
        self.file_label.pack(pady=5)

        # Metadata Entries
        self.entries = {}
        metadata_fields = ["Title", "Artist", "Album", "Year", "Comment", "Genre"]
        
        for field in metadata_fields:
            frame = ctk.CTkFrame(main_frame)
            frame.pack(fill="x", padx=10, pady=5)
            label = ctk.CTkLabel(frame, text=f"{field}:", width=10)
            label.pack(side="left", padx=5)
            entry = ctk.CTkEntry(frame)
            entry.pack(side="left", fill="x", expand=True, padx=5)
            self.entries[field] = entry

        # Save Button
        ctk.CTkButton(main_frame, text="Save Metadata", command=self.save_metadata).pack(pady=20)

    def load_video(self):
        path = filedialog.askopenfilename(title="Select MP4 Video File", filetypes=[("MP4 files", "*.mp4")])
        if path:
            self.video_path = path
            self.file_label.configure(text=os.path.basename(path))
            self.display_metadata()

    def display_metadata(self):
        try:
            video = MP4(self.video_path)
            self.entries["Title"].delete(0, 'end')
            self.entries["Title"].insert(0, video.get('\xa9nam', [''])[0])
            self.entries["Artist"].delete(0, 'end')
            self.entries["Artist"].insert(0, video.get('\xa9ART', [''])[0])
            self.entries["Album"].delete(0, 'end')
            self.entries["Album"].insert(0, video.get('\xa9alb', [''])[0])
            self.entries["Year"].delete(0, 'end')
            self.entries["Year"].insert(0, video.get('\xa9day', [''])[0])
            self.entries["Comment"].delete(0, 'end')
            self.entries["Comment"].insert(0, video.get('\xa9cmt', [''])[0])
            self.entries["Genre"].delete(0, 'end')
            self.entries["Genre"].insert(0, video.get('\xa9gen', [''])[0])
        except Exception as e:
            messagebox.showerror("Error", f"Could not read metadata: {e}")

    def save_metadata(self):
        if not self.video_path:
            messagebox.showerror("Error", "No video file selected.")
            return
            
        try:
            video = MP4(self.video_path)
            video['\xa9nam'] = self.entries["Title"].get()
            video['\xa9ART'] = self.entries["Artist"].get()
            video['\xa9alb'] = self.entries["Album"].get()
            video['\xa9day'] = self.entries["Year"].get()
            video['\xa9cmt'] = self.entries["Comment"].get()
            video['\xa9gen'] = self.entries["Genre"].get()
            video.save()
            messagebox.showinfo("Success", "Metadata saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save metadata: {e}") 