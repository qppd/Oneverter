import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
from threading import Thread
from moviepy.editor import VideoFileClip
from .base_converter import BaseConverter
from utils.file_utils import get_media_info

class VideoConverter(BaseConverter):
    def get_supported_formats(self):
        return [".mp4", ".avi", ".mov", ".mkv", ".webm"]
        
    def convert(self, input_path, output_path, options):
        try:
            video = VideoFileClip(input_path)
            
            # Resolution
            if 'resolution' in options and options['resolution'] != 'Original':
                resolutions = {"1080p": [1920, 1080], "720p": [1280, 720], "480p": [854, 480]}
                video = video.resize(height=resolutions[options['resolution']][1])

            # FPS
            if 'fps' in options and options['fps'] != 'Original':
                video = video.set_fps(int(options['fps']))

            # Codec
            codec = options.get('codec', 'libx264')

            # Audio Extraction
            if 'extract_audio' in options and options['extract_audio']:
                audio_format = options.get('audio_format', 'mp3')
                audio_output_path = os.path.splitext(output_path)[0] + f".{audio_format}"
                video.audio.write_audiofile(audio_output_path)
                return f"Audio extracted to {audio_output_path}"

            video.write_videofile(output_path, codec=codec, threads=4)
            return f"Successfully converted {os.path.basename(input_path)} to {os.path.basename(output_path)}"

        except Exception as e:
            return f"Error converting {os.path.basename(input_path)}: {e}"

class VideoConverterUI:
    def __init__(self, parent):
        self.parent = parent
        self.files = []
        self.converter = VideoConverter()
        
        self.setup_ui()

    def setup_ui(self):
        self.parent.grid_rowconfigure(1, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)
        
        # --- Main Frame ---
        main_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # --- File Selection ---
        file_frame = ctk.CTkFrame(main_frame)
        file_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        file_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(file_frame, text="Add Files", command=self.add_files).grid(row=0, column=0, padx=10, pady=10)
        self.file_list_label = ctk.CTkLabel(file_frame, text="No files selected", anchor="w")
        self.file_list_label.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        ctk.CTkButton(file_frame, text="Clear", command=self.clear_files).grid(row=0, column=2, padx=10, pady=10)

        # --- Settings Tabs ---
        self.tab_view = ctk.CTkTabview(main_frame)
        self.tab_view.grid(row=1, column=0, sticky="nsew", pady=10)
        self.tab_view.add("Video")
        self.tab_view.add("Audio")
        
        self.create_video_settings(self.tab_view.tab("Video"))
        self.create_audio_settings(self.tab_view.tab("Audio"))
        
        # --- Conversion ---
        conversion_frame = ctk.CTkFrame(main_frame)
        conversion_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        conversion_frame.grid_columnconfigure(0, weight=1)

        self.progress_bar = ctk.CTkProgressBar(conversion_frame)
        self.progress_bar.set(0)
        self.progress_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        ctk.CTkButton(conversion_frame, text="Convert", command=self.start_conversion_thread).grid(row=0, column=1, padx=10, pady=10)

        self.status_label = ctk.CTkLabel(main_frame, text="", anchor="w")
        self.status_label.grid(row=3, column=0, sticky="ew", padx=10, pady=10)

    def create_video_settings(self, tab):
        tab.grid_columnconfigure(1, weight=1)

        # Output Format
        ctk.CTkLabel(tab, text="Output Format:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.output_format = ctk.CTkOptionMenu(tab, values=["mp4", "avi", "webm", "gif"])
        self.output_format.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # Resolution
        ctk.CTkLabel(tab, text="Resolution:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.resolution = ctk.CTkOptionMenu(tab, values=["Original", "1080p", "720p", "480p"])
        self.resolution.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        # FPS
        ctk.CTkLabel(tab, text="FPS:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.fps = ctk.CTkOptionMenu(tab, values=["Original", "15", "30", "60"])
        self.fps.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

        # Codec
        ctk.CTkLabel(tab, text="Codec:").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.codec = ctk.CTkOptionMenu(tab, values=["h264", "libvpx-vp9", "mpeg4"])
        self.codec.grid(row=3, column=1, padx=10, pady=10, sticky="ew")

    def create_audio_settings(self, tab):
        tab.grid_columnconfigure(1, weight=1)
        self.extract_audio_var = ctk.BooleanVar()
        ctk.CTkCheckBox(tab, text="Extract Audio Only", variable=self.extract_audio_var, command=self.toggle_audio_extract).grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="w")

        self.audio_format_label = ctk.CTkLabel(tab, text="Audio Format:")
        self.audio_format_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.audio_format = ctk.CTkOptionMenu(tab, values=["mp3", "wav"])
        self.audio_format.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        self.toggle_audio_extract()

    def toggle_audio_extract(self):
        state = "normal" if self.extract_audio_var.get() else "disabled"
        self.audio_format_label.configure(state=state)
        self.audio_format.configure(state=state)

    def add_files(self):
        new_files = filedialog.askopenfilenames(
            title="Select Video Files",
            filetypes=[("Video Files", "*.mp4 *.avi *.mov *.mkv *.webm"), ("All files", "*.*")]
        )
        if new_files:
            self.files.extend(new_files)
            self.update_file_list_label()
    
    def clear_files(self):
        self.files = []
        self.update_file_list_label()
    
    def update_file_list_label(self):
        if not self.files:
            self.file_list_label.configure(text="No files selected")
        else:
            self.file_list_label.configure(text=f"{len(self.files)} files selected")

    def start_conversion_thread(self):
        thread = Thread(target=self.run_conversion)
        thread.start()

    def run_conversion(self):
        if not self.files:
            messagebox.showerror("Error", "No files selected for conversion.")
            return

        output_dir = filedialog.askdirectory(title="Select Output Folder")
        if not output_dir:
            return

        options = {
            "resolution": self.resolution.get(),
            "fps": self.fps.get(),
            "codec": self.codec.get(),
            "extract_audio": self.extract_audio_var.get(),
            "audio_format": self.audio_format.get()
        }
        
        total_files = len(self.files)
        for i, file_path in enumerate(self.files):
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            output_format = self.output_format.get()
            output_path = os.path.join(output_dir, f"{base_name}_converted.{output_format}")
            
            self.status_label.configure(text=f"Converting {os.path.basename(file_path)}...")
            
            try:
                result = self.converter.convert(file_path, output_path, options)
                self.status_label.configure(text=result)
            except Exception as e:
                self.status_label.configure(text=f"Error: {e}")
                
            progress = (i + 1) / total_files
            self.progress_bar.set(progress)
            
        messagebox.showinfo("Success", "All conversions finished!")
        self.progress_bar.set(0)
        self.status_label.configure(text="Finished.") 