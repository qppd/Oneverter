import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
from threading import Thread
from moviepy.editor import VideoFileClip
from .base_converter import BaseConverter

class FrameExtractor(BaseConverter):
    def get_supported_formats(self):
        return [".mp4", ".avi", ".mov", ".mkv", ".webm"]

    def convert(self, input_path, output_path, options):
        try:
            video = VideoFileClip(input_path)
            
            if options['method'] == 'interval':
                interval = options.get('interval', 1)
                for t in range(0, int(video.duration), interval):
                    frame_path = os.path.join(output_path, f"frame_at_{t}s.png")
                    video.save_frame(frame_path, t=t)
            elif options['method'] == 'fps':
                fps = options.get('fps', 1)
                video.write_images_sequence(os.path.join(output_path, "frame%04d.png"), fps=fps)

            video.close()
            return f"Successfully extracted frames from {os.path.basename(input_path)}"

        except Exception as e:
            return f"Error extracting frames: {e}"

class FrameExtractorUI:
    def __init__(self, parent):
        self.parent = parent
        self.video_path = None
        self.extractor = FrameExtractor()
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

        # --- Extraction Tabs ---
        self.tab_view = ctk.CTkTabview(main_frame)
        self.tab_view.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=10)
        self.tab_view.add("By Interval")
        self.tab_view.add("By FPS")
        
        self.create_interval_tab(self.tab_view.tab("By Interval"))
        self.create_fps_tab(self.tab_view.tab("By FPS"))

        # --- Conversion ---
        conversion_frame = ctk.CTkFrame(main_frame)
        conversion_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        conversion_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkButton(conversion_frame, text="Extract Frames", command=self.start_process_thread).grid(row=0, column=1, padx=10, pady=10)

        self.status_label = ctk.CTkLabel(main_frame, text="", anchor="w")
        self.status_label.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

    def create_interval_tab(self, tab):
        tab.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(tab, text="Interval (s):").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.interval_entry = ctk.CTkEntry(tab, placeholder_text="1")
        self.interval_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

    def create_fps_tab(self, tab):
        tab.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(tab, text="FPS:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.fps_entry = ctk.CTkEntry(tab, placeholder_text="1")
        self.fps_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

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

        method = 'interval' if self.tab_view.get() == "By Interval" else 'fps'
        options = {'method': method}
        
        try:
            if method == 'interval':
                options['interval'] = int(self.interval_entry.get())
            else:
                options['fps'] = int(self.fps_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid number for interval or FPS.")
            return

        output_dir = filedialog.askdirectory(title="Select Output Folder for Frames")
        if not output_dir:
            return
            
        self.status_label.configure(text=f"Extracting frames...")
        
        try:
            result = self.extractor.convert(self.video_path, output_dir, options)
            self.status_label.configure(text=result)
            messagebox.showinfo("Success", "Frames extracted successfully!")
        except Exception as e:
            self.status_label.configure(text=f"Error: {e}")
            messagebox.showerror("Error", f"An error occurred: {e}") 