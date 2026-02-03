import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
from threading import Thread
from moviepy import VideoFileClip, TextClip, CompositeVideoClip, ImageClip
from .base_converter import BaseConverter

class VideoWatermarker(BaseConverter):
    def get_supported_formats(self):
        return [".mp4", ".avi", ".mov", ".mkv", ".webm"]

    def convert(self, input_path, output_path, options):
        try:
            video = VideoFileClip(input_path)
            
            if options.get('type') == 'text':
                txt_clip = (TextClip(options.get('text'), fontsize=options.get('size', 24), color='white')
                            .set_position(options.get('position', 'center'))
                            .set_duration(video.duration)
                            .set_opacity(options.get('opacity', 0.8)))
                result = CompositeVideoClip([video, txt_clip])
            elif options.get('type') == 'logo':
                logo = (ImageClip(options.get('logo_path'))
                        .set_duration(video.duration)
                        .resize(height=options.get('scale', 50)) 
                        .set_opacity(options.get('opacity', 0.8))
                        .set_pos(options.get('position', 'center')))
                result = CompositeVideoClip([video, logo])
            else:
                raise ValueError("Invalid watermark type")

            result.write_videofile(output_path, codec='libx264')
            video.close()
            result.close()
            
            return f"Successfully watermarked {os.path.basename(input_path)}"

        except Exception as e:
            return f"Error watermarking video: {e}"

class VideoWatermarkerUI:
    def __init__(self, parent):
        self.parent = parent
        self.video_path = None
        self.logo_path = None
        self.watermarker = VideoWatermarker()
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

        # --- Watermark Tabs ---
        self.tab_view = ctk.CTkTabview(main_frame)
        self.tab_view.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=10)
        self.tab_view.add("Text")
        self.tab_view.add("Logo")
        
        self.create_text_tab(self.tab_view.tab("Text"))
        self.create_logo_tab(self.tab_view.tab("Logo"))

        # --- Conversion ---
        conversion_frame = ctk.CTkFrame(main_frame)
        conversion_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        conversion_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkButton(conversion_frame, text="Add Watermark", command=self.start_process_thread).grid(row=0, column=1, padx=10, pady=10)

        self.status_label = ctk.CTkLabel(main_frame, text="", anchor="w")
        self.status_label.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

    def create_text_tab(self, tab):
        tab.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(tab, text="Text:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.text_entry = ctk.CTkEntry(tab, placeholder_text="Your watermark text")
        self.text_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        ctk.CTkLabel(tab, text="Size:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.text_size_entry = ctk.CTkEntry(tab, placeholder_text="24")
        self.text_size_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        self.add_common_settings(tab, 2)

    def create_logo_tab(self, tab):
        tab.grid_columnconfigure(1, weight=1)
        ctk.CTkButton(tab, text="Select Logo", command=self.select_logo).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.logo_label = ctk.CTkLabel(tab, text="No logo selected")
        self.logo_label.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(tab, text="Scale (%):").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.logo_scale_entry = ctk.CTkEntry(tab, placeholder_text="10")
        self.logo_scale_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        
        self.add_common_settings(tab, 2)

    def add_common_settings(self, tab, start_row):
        ctk.CTkLabel(tab, text="Position:").grid(row=start_row, column=0, padx=10, pady=10, sticky="w")
        self.position_menu = ctk.CTkOptionMenu(tab, values=["top_left", "top_right", "bottom_left", "bottom_right", "center"])
        self.position_menu.grid(row=start_row, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(tab, text="Opacity (0-1):").grid(row=start_row + 1, column=0, padx=10, pady=10, sticky="w")
        self.opacity_entry = ctk.CTkEntry(tab, placeholder_text="0.8")
        self.opacity_entry.grid(row=start_row + 1, column=1, padx=10, pady=10, sticky="ew")

    def select_video(self):
        path = filedialog.askopenfilename(title="Select Video File")
        if path:
            self.video_path = path
            self.video_label.configure(text=os.path.basename(path))

    def select_logo(self):
        path = filedialog.askopenfilename(title="Select Logo File")
        if path:
            self.logo_path = path
            self.logo_label.configure(text=os.path.basename(path))
            
    def start_process_thread(self):
        thread = Thread(target=self.run_process)
        thread.start()
        
    def run_process(self):
        if not self.video_path:
            messagebox.showerror("Error", "Please select a video file.")
            return

        watermark_type = self.tab_view.get().lower()
        options = {'type': watermark_type}
        
        try:
            options['position'] = self.position_menu.get()
            options['opacity'] = float(self.opacity_entry.get())
            if watermark_type == 'text':
                options['text'] = self.text_entry.get()
                options['size'] = int(self.text_size_entry.get())
            elif watermark_type == 'logo':
                if not self.logo_path:
                    messagebox.showerror("Error", "Please select a logo file.")
                    return
                options['logo_path'] = self.logo_path
                options['scale'] = int(self.logo_scale_entry.get())

        except ValueError:
            messagebox.showerror("Error", "Invalid settings for watermark.")
            return

        output_path = filedialog.asksaveasfilename(
            defaultextension=".mp4",
            title="Save Watermarked Video As..."
        )
        if not output_path:
            return
            
        self.status_label.configure(text=f"Adding watermark...")
        
        try:
            result = self.watermarker.convert(self.video_path, output_path, options)
            self.status_label.configure(text=result)
            messagebox.showinfo("Success", "Video watermarked successfully!")
        except Exception as e:
            self.status_label.configure(text=f"Error: {e}")
            messagebox.showerror("Error", f"An error occurred: {e}") 