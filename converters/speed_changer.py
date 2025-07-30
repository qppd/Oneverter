import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
from threading import Thread
from moviepy.editor import VideoFileClip, vfx
from .base_converter import BaseConverter

class SpeedChanger(BaseConverter):
    def get_supported_formats(self):
        return [".mp4", ".avi", ".mov", ".mkv", ".webm"]

    def convert(self, input_path, output_path, options):
        try:
            video = VideoFileClip(input_path)
            speed = options.get('speed', 1.0)
            
            final_clip = video.fx(vfx.speedx, speed)
            
            final_clip.write_videofile(output_path, codec='libx264')
            
            video.close()
            final_clip.close()
            
            return f"Successfully changed speed of {os.path.basename(input_path)}"

        except Exception as e:
            return f"Error changing speed: {e}"

class SpeedChangerUI:
    def __init__(self, parent):
        self.parent = parent
        self.video_path = None
        self.tool = SpeedChanger()
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

        ctk.CTkLabel(settings_frame, text="Playback Speed:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.speed_menu = ctk.CTkOptionMenu(settings_frame, values=["0.5x", "0.75x", "1.0x", "1.25x", "1.5x", "2.0x"])
        self.speed_menu.set("1.0x")
        self.speed_menu.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # --- Conversion ---
        conversion_frame = ctk.CTkFrame(main_frame)
        conversion_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        conversion_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkButton(conversion_frame, text="Change Speed", command=self.start_process_thread).grid(row=0, column=1, padx=10, pady=10)

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
            speed_str = self.speed_menu.get().replace('x', '')
            speed = float(speed_str)
            options = {'speed': speed}
        except ValueError:
            messagebox.showerror("Error", "Invalid speed selected.")
            return

        output_path = filedialog.asksaveasfilename(
            defaultextension=".mp4",
            title="Save Video With New Speed As..."
        )
        if not output_path:
            return
            
        self.status_label.configure(text=f"Changing speed...")
        
        try:
            result = self.tool.convert(self.video_path, output_path, options)
            self.status_label.configure(text=result)
            messagebox.showinfo("Success", "Speed changed successfully!")
        except Exception as e:
            self.status_label.configure(text=f"Error: {e}")
            messagebox.showerror("Error", f"An error occurred: {e}") 