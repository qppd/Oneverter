import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
from threading import Thread
from moviepy.editor import VideoFileClip
from .base_converter import BaseConverter

class VideoTrimmer(BaseConverter):
    def get_supported_formats(self):
        return [".mp4", ".avi", ".mov", ".mkv", ".webm"]

    def convert(self, input_path, output_path, options):
        try:
            video = VideoFileClip(input_path)
            start_time = options.get('start_time', 0)
            end_time = options.get('end_time', video.duration)
            
            trimmed_video = video.subclip(start_time, end_time)
            trimmed_video.write_videofile(output_path, codec='libx264')
            
            return f"Successfully trimmed {os.path.basename(input_path)}"

        except Exception as e:
            return f"Error trimming {os.path.basename(input_path)}: {e}"

class VideoTrimmerUI:
    def __init__(self, parent):
        self.parent = parent
        self.file_path = None
        self.trimmer = VideoTrimmer()
        self.setup_ui()

    def setup_ui(self):
        self.parent.grid_rowconfigure(0, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)

        main_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)

        # File Selection
        file_frame = ctk.CTkFrame(main_frame)
        file_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        file_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkButton(file_frame, text="Select Video", command=self.select_file).grid(row=0, column=0, padx=10, pady=10)
        self.file_label = ctk.CTkLabel(file_frame, text="No video selected", anchor="w")
        self.file_label.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # Trim Settings
        settings_frame = ctk.CTkFrame(main_frame)
        settings_frame.grid(row=1, column=0, sticky="ew", pady=10)
        settings_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(settings_frame, text="Start Time (s):").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.start_time_entry = ctk.CTkEntry(settings_frame, placeholder_text="0")
        self.start_time_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(settings_frame, text="End Time (s):").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.end_time_entry = ctk.CTkEntry(settings_frame, placeholder_text="e.g., 60")
        self.end_time_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        
        # --- Conversion ---
        conversion_frame = ctk.CTkFrame(main_frame)
        conversion_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        conversion_frame.grid_columnconfigure(0, weight=1)

        self.progress_bar = ctk.CTkProgressBar(conversion_frame)
        self.progress_bar.set(0)
        self.progress_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        ctk.CTkButton(conversion_frame, text="Trim", command=self.start_trim_thread).grid(row=0, column=1, padx=10, pady=10)

        self.status_label = ctk.CTkLabel(main_frame, text="", anchor="w")
        self.status_label.grid(row=3, column=0, sticky="ew", padx=10, pady=10)

    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[("Video Files", "*.mp4 *.avi *.mov *.mkv *.webm"), ("All files", "*.*")]
        )
        if file_path:
            self.file_path = file_path
            self.file_label.configure(text=os.path.basename(file_path))

    def start_trim_thread(self):
        thread = Thread(target=self.run_trim)
        thread.start()
        
    def run_trim(self):
        if not self.file_path:
            messagebox.showerror("Error", "No video selected.")
            return
        
        try:
            start_time = float(self.start_time_entry.get() or 0)
            end_time = float(self.end_time_entry.get() or 'inf')
        except ValueError:
            messagebox.showerror("Error", "Invalid start or end time.")
            return
            
        output_path = filedialog.asksaveasfilename(
            defaultextension=".mp4",
            filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")],
            title="Save Trimmed Video As..."
        )
        if not output_path:
            return
            
        options = {"start_time": start_time, "end_time": end_time}
        
        self.status_label.configure(text=f"Trimming {os.path.basename(self.file_path)}...")
        self.progress_bar.set(0.5)

        try:
            result = self.trimmer.convert(self.file_path, output_path, options)
            self.status_label.configure(text=result)
            messagebox.showinfo("Success", "Video trimmed successfully!")
        except Exception as e:
            self.status_label.configure(text=f"Error: {e}")
            messagebox.showerror("Error", f"An error occurred: {e}")
        
        self.progress_bar.set(1)
        self.progress_bar.set(0) 