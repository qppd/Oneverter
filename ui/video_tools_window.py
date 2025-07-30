import customtkinter as ctk
from .base_window import BaseWindow
from converters.video_converter import VideoConverterUI
from converters.video_trimmer import VideoTrimmerUI
from converters.video_merger import VideoMergerUI
from converters.video_audio_editor import VideoAudioEditorUI
from converters.video_resizer import VideoResizerUI
from converters.video_watermarker import VideoWatermarkerUI
from converters.video_to_gif_converter import VideoToGifConverterUI
from converters.frame_extractor import FrameExtractorUI
from converters.subtitle_tool import SubtitleToolUI
from converters.speed_changer import SpeedChangerUI
from converters.youtube_downloader import YouTubeDownloaderUI
from converters.screen_recorder import ScreenRecorderUI

class VideoToolsWindow(BaseWindow):
    """Main window for all video tools."""

    def __init__(self, parent):
        super().__init__(parent, title="Oneverter - Video Tools", geometry="1280x720")
        self.resizable(True, True)
        self.minsize(900, 700)
        self.setup_ui()

    def setup_ui(self):
        """Setup the main UI with a responsive grid layout."""
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Header
        header_frame = ctk.CTkFrame(self)
        header_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")

        # Back button
        back_button = ctk.CTkButton(
            header_frame, text="← Back to Converters", command=self.on_close, width=150
        )
        back_button.pack(side="left")

        # Title
        title_label = ctk.CTkLabel(
            header_frame, text="🛠️ Video Tools", font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(side="left", padx=20)

        # Scrollable content area for tool cards
        self.scrollable_frame = ctk.CTkScrollableFrame(self)
        self.scrollable_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        
        self.create_tool_cards()

    def create_tool_cards(self):
        """Create cards for each video tool."""
        tools = [
            {"icon": "🎥", "title": "Video Converter", "desc": "Convert formats, change resolution, codec, FPS", "command": self.open_video_converter},
            {"icon": "✂️", "title": "Trim & Cut", "desc": "Cut out parts of a video", "command": self.open_video_trimmer},
            {"icon": "🔗", "title": "Merge Videos", "desc": "Combine multiple videos into one", "command": self.open_video_merger},
            {"icon": "🎶", "title": "Add/Remove Audio", "desc": "Mute, replace, or add audio tracks", "command": self.open_audio_editor},
            {"icon": "🖼️", "title": "Resize / Crop", "desc": "Change video dimensions or crop area", "command": self.open_video_resizer},
            {"icon": "✍️", "title": "Add Text/Watermark", "desc": "Overlay text or a logo", "command": self.open_video_watermarker},
            {"icon": "🔄", "title": "Convert to GIF", "desc": "Create animated GIFs from videos", "command": self.open_gif_converter},
            {"icon": "🎞️", "title": "Extract Frames", "desc": "Save video frames as images", "command": self.open_frame_extractor},
            {"icon": "🔤", "title": "Subtitle Tool", "desc": "Add or burn-in subtitles", "command": self.open_subtitle_tool},
            {"icon": "⏩", "title": "Playback Speed", "desc": "Change video playback speed", "command": self.open_speed_changer},
            {"icon": "📥", "title": "YouTube Downloader", "desc": "Download videos from YouTube", "command": self.open_youtube_downloader},
            {"icon": "⏺️", "title": "Screen Recorder", "desc": "Record your screen with audio", "command": self.open_screen_recorder},
        ]

        # Make the grid responsive
        for i in range(4):
            self.scrollable_frame.grid_columnconfigure(i, weight=1)

        for i, tool in enumerate(tools):
            row = i // 4
            col = i % 4
            self.create_card(
                self.scrollable_frame, row, col,
                tool["icon"], tool["title"], tool["desc"],
                tool["command"]
            )
            
    def create_card(self, parent, row, col, icon, title, description, command):
        """Creates a clickable card for a tool."""
        card = ctk.CTkFrame(parent, corner_radius=10, border_width=1)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

        card_button = ctk.CTkButton(
            card,
            text=f"{icon} {title}",
            command=command,
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        )
        card_button.pack(fill="x", padx=15, pady=(15, 5))

        desc_label = ctk.CTkLabel(
            card,
            text=description,
            wraplength=200,
            justify="left",
            anchor="w"
        )
        desc_label.pack(fill="x", padx=15, pady=(0, 15))

    def open_video_converter(self):
        # Clear the current view and show the converter UI
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        self.scrollable_frame.grid_columnconfigure(1, weight=0)
        self.scrollable_frame.grid_columnconfigure(2, weight=0)
        self.scrollable_frame.grid_columnconfigure(3, weight=0)

        # Instantiate the UI class, passing the scrollable frame as the parent
        self.video_converter_ui = VideoConverterUI(self.scrollable_frame)

    def open_video_trimmer(self):
        # Clear the current view and show the trimmer UI
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        self.scrollable_frame.grid_columnconfigure(1, weight=0)
        self.scrollable_frame.grid_columnconfigure(2, weight=0)
        self.scrollable_frame.grid_columnconfigure(3, weight=0)

        # Instantiate the UI class, passing the scrollable frame as the parent
        self.video_trimmer_ui = VideoTrimmerUI(self.scrollable_frame)

    def open_video_merger(self):
        # Clear the current view and show the merger UI
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        self.scrollable_frame.grid_columnconfigure(1, weight=0)
        self.scrollable_frame.grid_columnconfigure(2, weight=0)
        self.scrollable_frame.grid_columnconfigure(3, weight=0)

        # Instantiate the UI class, passing the scrollable frame as the parent
        self.video_merger_ui = VideoMergerUI(self.scrollable_frame)

    def open_audio_editor(self):
        # Clear the current view and show the audio editor UI
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        self.scrollable_frame.grid_columnconfigure(1, weight=0)
        self.scrollable_frame.grid_columnconfigure(2, weight=0)
        self.scrollable_frame.grid_columnconfigure(3, weight=0)

        # Instantiate the UI class, passing the scrollable frame as the parent
        self.video_audio_editor_ui = VideoAudioEditorUI(self.scrollable_frame)

    def open_video_resizer(self):
        # Clear the current view and show the resizer UI
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        self.scrollable_frame.grid_columnconfigure(1, weight=0)
        self.scrollable_frame.grid_columnconfigure(2, weight=0)
        self.scrollable_frame.grid_columnconfigure(3, weight=0)

        # Instantiate the UI class, passing the scrollable frame as the parent
        self.video_resizer_ui = VideoResizerUI(self.scrollable_frame)

    def open_video_watermarker(self):
        # Clear the current view and show the watermarker UI
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        self.scrollable_frame.grid_columnconfigure(1, weight=0)
        self.scrollable_frame.grid_columnconfigure(2, weight=0)
        self.scrollable_frame.grid_columnconfigure(3, weight=0)

        # Instantiate the UI class, passing the scrollable frame as the parent
        self.video_watermarker_ui = VideoWatermarkerUI(self.scrollable_frame)

    def open_gif_converter(self):
        # Clear the current view and show the gif converter UI
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        self.scrollable_frame.grid_columnconfigure(1, weight=0)
        self.scrollable_frame.grid_columnconfigure(2, weight=0)
        self.scrollable_frame.grid_columnconfigure(3, weight=0)

        # Instantiate the UI class, passing the scrollable frame as the parent
        self.video_to_gif_converter_ui = VideoToGifConverterUI(self.scrollable_frame)

    def open_frame_extractor(self):
        # Clear the current view and show the frame extractor UI
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        self.scrollable_frame.grid_columnconfigure(1, weight=0)
        self.scrollable_frame.grid_columnconfigure(2, weight=0)
        self.scrollable_frame.grid_columnconfigure(3, weight=0)

        # Instantiate the UI class, passing the scrollable frame as the parent
        self.frame_extractor_ui = FrameExtractorUI(self.scrollable_frame)

    def open_subtitle_tool(self):
        # Clear the current view and show the subtitle tool UI
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        self.scrollable_frame.grid_columnconfigure(1, weight=0)
        self.scrollable_frame.grid_columnconfigure(2, weight=0)
        self.scrollable_frame.grid_columnconfigure(3, weight=0)

        # Instantiate the UI class, passing the scrollable frame as the parent
        self.subtitle_tool_ui = SubtitleToolUI(self.scrollable_frame)

    def open_speed_changer(self):
        # Clear the current view and show the speed changer UI
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        self.scrollable_frame.grid_columnconfigure(1, weight=0)
        self.scrollable_frame.grid_columnconfigure(2, weight=0)
        self.scrollable_frame.grid_columnconfigure(3, weight=0)

        # Instantiate the UI class, passing the scrollable frame as the parent
        self.speed_changer_ui = SpeedChangerUI(self.scrollable_frame)

    def open_youtube_downloader(self):
        # Clear the current view and show the youtube downloader UI
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        self.scrollable_frame.grid_columnconfigure(1, weight=0)
        self.scrollable_frame.grid_columnconfigure(2, weight=0)
        self.scrollable_frame.grid_columnconfigure(3, weight=0)

        # Instantiate the UI class, passing the scrollable frame as the parent
        self.youtube_downloader_ui = YouTubeDownloaderUI(self.scrollable_frame)

    def open_screen_recorder(self):
        # Clear the current view and show the screen recorder UI
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        self.scrollable_frame.grid_columnconfigure(1, weight=0)
        self.scrollable_frame.grid_columnconfigure(2, weight=0)
        self.scrollable_frame.grid_columnconfigure(3, weight=0)

        # Instantiate the UI class, passing the scrollable frame as the parent
        self.screen_recorder_ui = ScreenRecorderUI(self.scrollable_frame)

    def open_tool(self, tool_name):
        """Placeholder for opening other tools."""
        print(f"Opening {tool_name}...") 