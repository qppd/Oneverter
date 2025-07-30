import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
from threading import Thread
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from .base_converter import BaseConverter
import pysrt

class SubtitleTool(BaseConverter):
    def get_supported_formats(self):
        return [".mp4", ".avi", ".mov", ".mkv", ".webm"]

    def convert(self, input_path, output_path, options):
        try:
            video = VideoFileClip(input_path)
            subs = pysrt.open(options['subtitle_path'], encoding='utf-8')

            clips = [video]
            for sub in subs:
                txt_clip = TextClip(sub.text, fontsize=options.get('font_size', 24), color='yellow',
                                    stroke_color='black', stroke_width=1, font='Arial',
                                    size=(video.w*0.8, None), method='caption')
                
                txt_clip = txt_clip.set_pos(('center', 'bottom')).set_duration(sub.duration.to_seconds()).set_start(sub.start.to_seconds())
                clips.append(txt_clip)

            result = CompositeVideoClip(clips)
            result.write_videofile(output_path, codec="libx264", audio_codec="aac")
            
            video.close()
            result.close()
            return f"Successfully added subtitles to {os.path.basename(input_path)}"

        except Exception as e:
            return f"Error adding subtitles: {e}"

class SubtitleToolUI:
    def __init__(self, parent):
        self.parent = parent
        self.video_path = None
        self.subtitle_path = None
        self.tool = SubtitleTool()
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

        ctk.CTkButton(main_frame, text="Select Subtitle File (.srt)", command=self.select_subtitle).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.subtitle_label = ctk.CTkLabel(main_frame, text="No subtitle file selected")
        self.subtitle_label.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        # --- Settings ---
        settings_frame = ctk.CTkFrame(main_frame)
        settings_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=10)
        settings_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(settings_frame, text="Font Size:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.font_size_entry = ctk.CTkEntry(settings_frame, placeholder_text="24")
        self.font_size_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # --- Conversion ---
        conversion_frame = ctk.CTkFrame(main_frame)
        conversion_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        conversion_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkButton(conversion_frame, text="Add Subtitles", command=self.start_process_thread).grid(row=0, column=1, padx=10, pady=10)

        self.status_label = ctk.CTkLabel(main_frame, text="", anchor="w")
        self.status_label.grid(row=4, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

    def select_video(self):
        path = filedialog.askopenfilename(title="Select Video File")
        if path:
            self.video_path = path
            self.video_label.configure(text=os.path.basename(path))
            
    def select_subtitle(self):
        path = filedialog.askopenfilename(title="Select Subtitle File", filetypes=[("SRT files", "*.srt")])
        if path:
            self.subtitle_path = path
            self.subtitle_label.configure(text=os.path.basename(path))
            
    def start_process_thread(self):
        thread = Thread(target=self.run_process)
        thread.start()
        
    def run_process(self):
        if not self.video_path or not self.subtitle_path:
            messagebox.showerror("Error", "Please select a video and a subtitle file.")
            return

        try:
            options = {'subtitle_path': self.subtitle_path, 'font_size': int(self.font_size_entry.get() or 24)}
        except ValueError:
            messagebox.showerror("Error", "Invalid font size.")
            return

        output_path = filedialog.asksaveasfilename(
            defaultextension=".mp4",
            title="Save Subtitled Video As..."
        )
        if not output_path:
            return
            
        self.status_label.configure(text=f"Adding subtitles...")
        
        try:
            result = self.tool.convert(self.video_path, output_path, options)
            self.status_label.configure(text=result)
            messagebox.showinfo("Success", "Subtitles added successfully!")
        except Exception as e:
            self.status_label.configure(text=f"Error: {e}")
            messagebox.showerror("Error", f"An error occurred: {e}") 