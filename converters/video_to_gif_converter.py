import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
from threading import Thread
from moviepy import VideoFileClip
from .base_converter import BaseConverter

class VideoToGifConverter(BaseConverter):
    def get_supported_formats(self):
        return [".mp4", ".avi", ".mov", ".mkv", ".webm"]

    def convert(self, input_path, output_path, options):
        try:
            video = VideoFileClip(input_path).subclip(options.get('start', 0), options.get('end', None))
            
            if options.get('resize'):
                video = video.resize(width=options.get('width'))

            video.write_gif(output_path, fps=options.get('fps', 10), loop=options.get('loop', 0))
            video.close()
            
            return f"Successfully converted {os.path.basename(input_path)} to GIF"

        except Exception as e:
            return f"Error converting to GIF: {e}"

class VideoToGifConverterUI:
    def __init__(self, parent):
        self.parent = parent
        self.video_path = None
        self.converter = VideoToGifConverter()
        self.setup_ui()

    def setup_ui(self):
        self.parent.grid_rowconfigure(0, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)

        main_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)

        # File Selection
        ctk.CTkButton(main_frame, text="Select Video", command=self.select_video).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.video_label = ctk.CTkLabel(main_frame, text="No video selected")
        self.video_label.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # --- Settings ---
        settings_frame = ctk.CTkFrame(main_frame)
        settings_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=10)
        settings_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(settings_frame, text="Start Time (s):").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.start_time_entry = ctk.CTkEntry(settings_frame, placeholder_text="0")
        self.start_time_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(settings_frame, text="End Time (s):").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.end_time_entry = ctk.CTkEntry(settings_frame, placeholder_text="e.g., 5")
        self.end_time_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(settings_frame, text="FPS:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.fps_entry = ctk.CTkEntry(settings_frame, placeholder_text="10")
        self.fps_entry.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

        self.loop_var = ctk.BooleanVar()
        ctk.CTkCheckBox(settings_frame, text="Loop GIF", variable=self.loop_var).grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="w")

        # --- Conversion ---
        conversion_frame = ctk.CTkFrame(main_frame)
        conversion_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        conversion_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkButton(conversion_frame, text="Convert to GIF", command=self.start_process_thread).grid(row=0, column=1, padx=10, pady=10)

        self.status_label = ctk.CTkLabel(main_frame, text="", anchor="w")
        self.status_label.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

    def select_video(self):
        path = filedialog.askopenfilename(title="Select Video File")
        if path:
            self.video_path = path
            self.video_label.configure(text=os.path.basename(path))
            
    def start_process_thread(self):
        thread = Thread(target=self.run_process)
        thread.start()
        
    def run_process(self):
        if not self.video_path:
            messagebox.showerror("Error", "Please select a video file.")
            return

        try:
            options = {
                'start': float(self.start_time_entry.get() or 0),
                'end': float(self.end_time_entry.get() or 'inf'),
                'fps': int(self.fps_entry.get() or 10),
                'loop': 1 if self.loop_var.get() else 0
            }
        except ValueError:
            messagebox.showerror("Error", "Invalid settings for GIF conversion.")
            return

        output_path = filedialog.asksaveasfilename(
            defaultextension=".gif",
            title="Save GIF As..."
        )
        if not output_path:
            return
            
        self.status_label.configure(text=f"Converting to GIF...")
        
        try:
            result = self.converter.convert(self.video_path, output_path, options)
            self.status_label.configure(text=result)
            messagebox.showinfo("Success", "GIF conversion successful!")
        except Exception as e:
            self.status_label.configure(text=f"Error: {e}")
            messagebox.showerror("Error", f"An error occurred: {e}") 