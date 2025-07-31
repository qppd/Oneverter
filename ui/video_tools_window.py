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
from converters.metadata_editor import MetadataEditorUI

class VideoToolsWindow(BaseWindow):
    """Main window for all video tools with advanced editing capabilities."""

    def __init__(self, parent):
        super().__init__(parent, title="Oneverter - Video Studio", geometry="1280x720")
        self.resizable(True, True)
        self.minsize(1024, 768)  # Larger minimum size for better UI experience
        self.setup_ui()

    def setup_ui(self):
        """Setup the main UI with a modern tabbed interface."""
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Header with modern styling
        header_frame = ctk.CTkFrame(self)
        header_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")

        # Back button with updated style
        back_button = ctk.CTkButton(
            header_frame, 
            text="← Back to Converters", 
            command=self.on_close, 
            width=150,
            fg_color=("#2B2B2B", "#3E3E3E"),  # Darker theme
            hover_color=("#363636", "#4A4A4A")
        )
        back_button.pack(side="left")

        # Modern title with icon
        title_label = ctk.CTkLabel(
            header_frame, 
            text="🎬 Oneverter Studio", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(side="left", padx=20)

        # Main content area with tabs
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        
        # Create main tabs
        self.quick_tools_tab = self.tab_view.add("Quick Tools")
        self.video_editor_tab = self.tab_view.add("Video Editor")
        self.screen_recorder_tab = self.tab_view.add("Screen Recorder")
        self.youtube_tools_tab = self.tab_view.add("YouTube Tools")

        # Setup content for each tab
        self.setup_quick_tools_tab()
        self.setup_video_editor_tab()
        self.setup_screen_recorder_tab()
        self.setup_youtube_tools_tab()

    def setup_quick_tools_tab(self):
        """Setup the Quick Tools tab with common video operations."""
        tools_frame = ctk.CTkFrame(self.quick_tools_tab)
        tools_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Create a grid of quick tools
        tools = [
            ("✂️ Trim Video", self.open_trimmer),
            ("🔄 Convert Format", self.open_converter),
            ("📏 Resize Video", self.open_resizer),
            ("🔀 Merge Videos", self.open_merger),
            ("🖼️ Extract Frames", self.open_frame_extractor),
            ("⚡ Change Speed", self.open_speed_changer),
            ("💧 Add Watermark", self.open_watermarker),
            ("🎯 GIF Converter", self.open_gif_converter)
        ]

        for i, (tool_name, command) in enumerate(tools):
            row, col = divmod(i, 4)
            tool_frame = ctk.CTkFrame(tools_frame)
            tool_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            
            button = ctk.CTkButton(
                tool_frame,
                text=tool_name,
                command=command,
                width=200,
                height=100,
                font=ctk.CTkFont(size=16)
            )
            button.pack(padx=10, pady=10)

        # Configure grid
        for i in range(2):  # Rows
            tools_frame.grid_rowconfigure(i, weight=1)
        for i in range(4):  # Columns
            tools_frame.grid_columnconfigure(i, weight=1)

    def setup_video_editor_tab(self):
        """Setup the video editor tab with CapCut-style interface."""
        from .components.capcut_style_editor import CapcutStyleEditor

        # Create the CapCut-style editor
        self.video_editor = CapcutStyleEditor(self.video_editor_tab)
        self.video_editor.pack(fill="both", expand=True)

    def setup_screen_recorder_tab(self):
        """Setup the Screen Recorder tab with professional OBS-style features."""
        from .components.screen_recorder_components import ScreenRecorderPanel
        
        # Create the enhanced screen recorder panel
        self.screen_recorder = ScreenRecorderPanel(self.screen_recorder_tab)
        self.screen_recorder.pack(fill="both", expand=True, padx=10, pady=10)

    def setup_youtube_tools_tab(self):
        """Setup the YouTube Tools tab with download and upload features."""
        youtube_frame = ctk.CTkFrame(self.youtube_tools_tab)
        youtube_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # URL input
        url_frame = ctk.CTkFrame(youtube_frame)
        url_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(url_frame, text="YouTube URL:").pack(side="left", padx=5)
        url_entry = ctk.CTkEntry(url_frame, placeholder_text="Enter YouTube URL", width=400)
        url_entry.pack(side="left", padx=5, fill="x", expand=True)

        # Download options
        options_frame = ctk.CTkFrame(youtube_frame)
        options_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(options_frame, text="Quality:").pack(side="left", padx=5)
        quality_menu = ctk.CTkOptionMenu(options_frame, values=["Best", "1080p", "720p", "480p", "360p"])
        quality_menu.pack(side="left", padx=5)
        
        ctk.CTkLabel(options_frame, text="Format:").pack(side="left", padx=5)
        format_menu = ctk.CTkOptionMenu(options_frame, values=["MP4", "Audio Only (MP3)"])
        format_menu.pack(side="left", padx=5)

        # Action buttons
        action_frame = ctk.CTkFrame(youtube_frame)
        action_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(action_frame, text="Download", width=150).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="Advanced Options", width=150).pack(side="left", padx=5)

        # Download queue
        queue_frame = ctk.CTkFrame(youtube_frame)
        queue_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(queue_frame, text="Download Queue:").pack(anchor="w", padx=5, pady=5)
        
        # ...existing code...

    def create_tool_cards(self):
        """Create cards for each video tool."""
        tools = [
            {"icon": "🎥", "title": "Video Converter", "desc": "Convert video formats, resolution, codec, FPS", "command": self.open_video_converter},
            {"icon": "✂️", "title": "Trim & Cut", "desc": "Remove unwanted parts", "command": self.open_video_trimmer},
            {"icon": "🔗", "title": "Merge Videos", "desc": "Combine multiple videos", "command": self.open_video_merger},
            {"icon": "🎶", "title": "Audio Editor", "desc": "Mute, replace, or add audio", "command": self.open_audio_editor},
            {"icon": "🖼️", "title": "Resize / Crop", "desc": "Change dimensions or crop area", "command": self.open_video_resizer},
            {"icon": "✍️", "title": "Watermark/Text", "desc": "Overlay text or logo", "command": self.open_video_watermarker},
            {"icon": "🔄", "title": "GIF Converter", "desc": "Create GIFs from videos", "command": self.open_gif_converter},
            {"icon": "🎞️", "title": "Frame Extractor", "desc": "Save frames as images", "command": self.open_frame_extractor},
            {"icon": "🔤", "title": "Subtitle Tool", "desc": "Add or burn-in subtitles", "command": self.open_subtitle_tool},
            {"icon": "⏩", "title": "Speed Changer", "desc": "Adjust playback speed", "command": self.open_speed_changer},
            {"icon": "📥", "title": "YouTube Downloader", "desc": "Download YouTube videos", "command": self.open_youtube_downloader},
            {"icon": "📝", "title": "Metadata Editor", "desc": "Edit video metadata", "command": self.open_metadata_editor},
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

    def open_metadata_editor(self):
        # Clear the current view and show the metadata editor UI
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        self.scrollable_frame.grid_columnconfigure(1, weight=0)
        self.scrollable_frame.grid_columnconfigure(2, weight=0)
        self.scrollable_frame.grid_columnconfigure(3, weight=0)

        # Instantiate the UI class, passing the scrollable frame as the parent
        self.metadata_editor_ui = MetadataEditorUI(self.scrollable_frame)

    def open_tool(self, tool_name):
        """Placeholder for opening other tools."""
        print(f"Opening {tool_name}...") 