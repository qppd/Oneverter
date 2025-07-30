import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
from threading import Thread
from moviepy.editor import VideoFileClip, vfx
from .base_converter import BaseConverter

class VideoResizer(BaseConverter):
    def get_supported_formats(self):
        return [".mp4", ".avi", ".mov", ".mkv", ".webm"]

    def convert(self, input_path, output_path, options):
        try:
            video = VideoFileClip(input_path)
            
            if options.get('action') == 'resize':
                width = options.get('width')
                height = options.get('height')
                video = video.fx(vfx.resize, width=width, height=height)
            elif options.get('action') == 'crop':
                x1 = options.get('x1', 0)
                y1 = options.get('y1', 0)
                x2 = options.get('x2', video.w)
                y2 = options.get('y2', video.h)
                video = video.fx(vfx.crop, x1=x1, y1=y1, x2=x2, y2=y2)
            
            video.write_videofile(output_path, codec='libx264')
            video.close()
            
            return f"Successfully processed {os.path.basename(input_path)}"

        except Exception as e:
            return f"Error processing video: {e}"

class VideoResizerUI:
    def __init__(self, parent):
        self.parent = parent
        self.video_path = None
        self.resizer = VideoResizer()
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

        # --- Action Tabs ---
        self.tab_view = ctk.CTkTabview(main_frame)
        self.tab_view.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=10)
        self.tab_view.add("Resize")
        self.tab_view.add("Crop")
        
        self.create_resize_tab(self.tab_view.tab("Resize"))
        self.create_crop_tab(self.tab_view.tab("Crop"))

        # --- Conversion ---
        conversion_frame = ctk.CTkFrame(main_frame)
        conversion_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        conversion_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkButton(conversion_frame, text="Process", command=self.start_process_thread).grid(row=0, column=1, padx=10, pady=10)

        self.status_label = ctk.CTkLabel(main_frame, text="", anchor="w")
        self.status_label.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

    def create_resize_tab(self, tab):
        tab.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(tab, text="Width:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.resize_width_entry = ctk.CTkEntry(tab, placeholder_text="e.g., 1280")
        self.resize_width_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        ctk.CTkLabel(tab, text="Height:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.resize_height_entry = ctk.CTkEntry(tab, placeholder_text="e.g., 720")
        self.resize_height_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

    def create_crop_tab(self, tab):
        tab.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(tab, text="X1:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.crop_x1_entry = ctk.CTkEntry(tab, placeholder_text="e.g., 0")
        self.crop_x1_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        ctk.CTkLabel(tab, text="Y1:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.crop_y1_entry = ctk.CTkEntry(tab, placeholder_text="e.g., 0")
        self.crop_y1_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(tab, text="X2:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.crop_x2_entry = ctk.CTkEntry(tab, placeholder_text="e.g., 1920")
        self.crop_x2_entry.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(tab, text="Y2:").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.crop_y2_entry = ctk.CTkEntry(tab, placeholder_text="e.g., 1080")
        self.crop_y2_entry.grid(row=3, column=1, padx=10, pady=10, sticky="ew")
        
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

        action = self.tab_view.get().lower()
        options = {"action": action}
        
        try:
            if action == 'resize':
                options['width'] = int(self.resize_width_entry.get())
                options['height'] = int(self.resize_height_entry.get())
            elif action == 'crop':
                options['x1'] = int(self.crop_x1_entry.get())
                options['y1'] = int(self.crop_y1_entry.get())
                options['x2'] = int(self.crop_x2_entry.get())
                options['y2'] = int(self.crop_y2_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid dimensions for resize/crop.")
            return

        output_path = filedialog.asksaveasfilename(
            defaultextension=".mp4",
            title="Save Processed Video As..."
        )
        if not output_path:
            return
            
        self.status_label.configure(text=f"Processing video...")
        
        try:
            result = self.resizer.convert(self.video_path, output_path, options)
            self.status_label.configure(text=result)
            messagebox.showinfo("Success", "Video processed successfully!")
        except Exception as e:
            self.status_label.configure(text=f"Error: {e}")
            messagebox.showerror("Error", f"An error occurred: {e}") 