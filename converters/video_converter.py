import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
from threading import Thread
from moviepy import VideoFileClip
from .base_converter import BaseConverter
from .base_converter_ui import BaseConverterUI
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

class VideoConverterUI(BaseConverterUI):
    def __init__(self, parent_frame: ctk.CTkFrame):
        """Initialize the video converter UI."""
        self.converter = VideoConverter()
        super().__init__(parent_frame)

    def has_tabs(self) -> bool:
        """Video Tools uses tabs."""
        return True

    def setup_tabs(self):
        """Setup the video tools tabs."""
        # Main conversion tools
        self.converter_tab = self.tab_view.add("Video Converter")
        self.trimmer_tab = self.tab_view.add("Trim & Cut")
        self.merger_tab = self.tab_view.add("Merge Videos")
        
        # Enhancement tools
        self.resizer_tab = self.tab_view.add("Resize / Crop")
        self.watermark_tab = self.tab_view.add("Watermark")
        self.subtitle_tab = self.tab_view.add("Subtitles")
        
        # Special features
        self.gif_tab = self.tab_view.add("Convert to GIF")
        self.frame_tab = self.tab_view.add("Extract Frames")
        self.speed_tab = self.tab_view.add("Playback Speed")
        self.youtube_tab = self.tab_view.add("YouTube Download")
        self.screen_tab = self.tab_view.add("Screen Recorder")
        self.metadata_tab = self.tab_view.add("Metadata")

    def build_ui(self):
        """Build the UI using pack geometry manager consistently."""
        # --- Main Frame ---
        main_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # --- File Selection ---
        file_frame = ctk.CTkFrame(main_frame)
        file_frame.pack(fill="x", pady=(0, 10))
        
        # File selection buttons and label in horizontal layout
        button_frame = ctk.CTkFrame(file_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=10, pady=10)
        
        add_button = ctk.CTkButton(button_frame, text="Add Files", command=self.add_files)
        add_button.pack(side="left", padx=(0, 10))
        
        self.file_list_label = ctk.CTkLabel(button_frame, text="No files selected", anchor="w")
        self.file_list_label.pack(side="left", fill="x", expand=True)
        
        clear_button = ctk.CTkButton(button_frame, text="Clear", command=self.clear_files)
        clear_button.pack(side="right", padx=(10, 0))

        # --- Settings Tabs ---
        self.tab_view = ctk.CTkTabview(main_frame)
        self.tab_view.pack(fill="both", expand=True, pady=10)
        self.tab_view.add("Video")
        self.tab_view.add("Audio")
        
        self.create_video_settings(self.tab_view.tab("Video"))
        self.create_audio_settings(self.tab_view.tab("Audio"))
        
        # --- Conversion ---
        conversion_frame = ctk.CTkFrame(main_frame)
        conversion_frame.pack(fill="x", pady=(10, 0))

        # Progress and convert button in horizontal layout
        progress_frame = ctk.CTkFrame(conversion_frame, fg_color="transparent")
        progress_frame.pack(fill="x", padx=10, pady=10)
        
        self.progress_bar = ctk.CTkProgressBar(progress_frame)
        self.progress_bar.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.progress_bar.set(0)
        
        convert_button = ctk.CTkButton(progress_frame, text="Convert", command=self.start_conversion_thread)
        convert_button.pack(side="right")

        # Status label
        self.status_label = ctk.CTkLabel(main_frame, text="", anchor="w")
        self.status_label.pack(fill="x", padx=10, pady=10)

    def create_video_settings(self, tab):
        """Create video settings using pack geometry manager."""
        # Output Format
        format_frame = ctk.CTkFrame(tab, fg_color="transparent")
        format_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(format_frame, text="Output Format:").pack(side="left")
        self.output_format = ctk.CTkOptionMenu(format_frame, values=["mp4", "avi", "webm", "gif"])
        self.output_format.pack(side="left", padx=(10, 0), fill="x", expand=True)

        # Resolution
        resolution_frame = ctk.CTkFrame(tab, fg_color="transparent")
        resolution_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(resolution_frame, text="Resolution:").pack(side="left")
        self.resolution = ctk.CTkOptionMenu(resolution_frame, values=["Original", "1080p", "720p", "480p"])
        self.resolution.pack(side="left", padx=(10, 0), fill="x", expand=True)

        # FPS
        fps_frame = ctk.CTkFrame(tab, fg_color="transparent")
        fps_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(fps_frame, text="FPS:").pack(side="left")
        self.fps = ctk.CTkOptionMenu(fps_frame, values=["Original", "15", "30", "60"])
        self.fps.pack(side="left", padx=(10, 0), fill="x", expand=True)

        # Codec
        codec_frame = ctk.CTkFrame(tab, fg_color="transparent")
        codec_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(codec_frame, text="Codec:").pack(side="left")
        self.codec = ctk.CTkOptionMenu(codec_frame, values=["h264", "libvpx-vp9", "mpeg4"])
        self.codec.pack(side="left", padx=(10, 0), fill="x", expand=True)

    def create_audio_settings(self, tab):
        """Create audio settings using pack geometry manager."""
        # Extract Audio Checkbox
        self.extract_audio_var = ctk.BooleanVar()
        checkbox = ctk.CTkCheckBox(
            tab, 
            text="Extract Audio Only", 
            variable=self.extract_audio_var, 
            command=self.toggle_audio_extract
        )
        checkbox.pack(fill="x", padx=10, pady=10)

        # Audio Format
        format_frame = ctk.CTkFrame(tab, fg_color="transparent")
        format_frame.pack(fill="x", padx=10, pady=5)
        
        self.audio_format_label = ctk.CTkLabel(format_frame, text="Audio Format:")
        self.audio_format_label.pack(side="left")
        
        self.audio_format = ctk.CTkOptionMenu(format_frame, values=["mp3", "wav"])
        self.audio_format.pack(side="left", padx=(10, 0), fill="x", expand=True)
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