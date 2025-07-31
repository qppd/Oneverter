import customtkinter as ctk
from ..converter_panel import ConverterPanel
from ..components.capcut_style_editor import CapcutStyleEditor
from ..theme import Colors, get_frame_style
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

class VideoToolsPanel(ConverterPanel):
    """Modern video editing panel with CapCut-style interface."""
    
    def __init__(self, parent):
        # Initialize tools list before calling parent constructor
        self.tools = [
            {
                "icon": "🎶",
                "title": "Add/Remove Audio",
                "desc": "Mute, replace, or add audio tracks",
                "ui_class": VideoAudioEditorUI
            },
            {
                "icon": "🖼️",
                "title": "Resize / Crop",
                "desc": "Change video dimensions or crop area",
                "ui_class": VideoResizerUI
            },
            {
                "icon": "✍️",
                "title": "Add Text/Watermark",
                "desc": "Overlay text or a logo",
                "ui_class": VideoWatermarkerUI
            },
            {
                "icon": "🔄",
                "title": "Convert to GIF",
                "desc": "Create animated GIFs from videos",
                "ui_class": VideoToGifConverterUI
            },
            {
                "icon": "🎞️",
                "title": "Extract Frames",
                "desc": "Save video frames as images",
                "ui_class": FrameExtractorUI
            },
            {
                "icon": "🔤",
                "title": "Subtitle Tool",
                "desc": "Add or burn-in subtitles",
                "ui_class": SubtitleToolUI
            },
            {
                "icon": "⏩",
                "title": "Playback Speed",
                "desc": "Change video playback speed",
                "ui_class": SpeedChangerUI
            },
            {
                "icon": "📥",
                "title": "YouTube Downloader",
                "desc": "Download videos from YouTube",
                "ui_class": YouTubeDownloaderUI
            },
            {
                "icon": "⏺️",
                "title": "Screen Recorder",
                "desc": "Record your screen with audio",
                "ui_class": ScreenRecorderUI
            },
            {
                "icon": "📝",
                "title": "Metadata Editor",
                "desc": "Edit video title, author, etc.",
                "ui_class": MetadataEditorUI
            }
        ]
        
        # Initialize parent after tools list is created
        super().__init__(parent, category="Video", tool_name="", description="")  # Empty strings for no display
        # Hide default progress area as we don't need it for this panel
        self.progress_frame.grid_remove()
        self.setup_converter_ui()
        
    def setup_converter_ui(self):
        """Setup the modern video editing interface."""
        # Create tool cards section
        tools_section = self.create_section("Available Tools")
        tools_section.grid_columnconfigure((0,1,2,3), weight=1, uniform="col")
        
        # Create tool cards in a 4-column grid
        for i, tool in enumerate(self.tools):
            row = i // 4
            col = i % 4
            self.add_tool_card(
                tools_section,
                row, col,
                tool["icon"],
                tool["title"],
                tool["desc"],
                lambda ui_class=tool["ui_class"], title=tool["title"]: self.open_tool(title, ui_class)
            )
            
        # Main editor in the content area
        self.editor = CapcutStyleEditor(self.content_frame)
        self.editor.pack(fill="both", expand=True, padx=10, pady=10)
        
    def add_tool_card(self, parent, row, col, icon, title, desc, command):
        """Create a compact tool card with just icon and title."""
        card = ctk.CTkFrame(parent, **get_frame_style())
        card.grid(row=row, column=col, sticky="nsew", padx=2, pady=2)
        
        # Tool icon and title in a compact layout
        title_label = ctk.CTkLabel(
            card,
            text=f"{icon}  {title}",  # Added extra space for better icon-text separation
            font=ctk.CTkFont(size=13),
            text_color=Colors.TEXT
        )
        title_label.pack(fill="x", padx=8, pady=8)
        
        # Make the card clickable
        for widget in [card, title_label]:
            widget.bind("<Button-1>", lambda e: command())
    
    def refresh(self):
        """Refresh the panel state."""
        pass  # No refresh needed for this panel
        
    def show_tool_interface(self, tool_name: str, tool_ui_class):
        """Override to prevent the default tool interface behavior."""
        pass  # We don't want to show individual tools anymore
            
    def open_tool(self, tool_name: str, tool_ui_class):
        """Open a specific video tool."""
        self.show_tool_interface(tool_name, tool_ui_class)
        
        # Update navigation
        if hasattr(self.parent, 'navigation_manager'):
            self.parent.navigation_manager.navigate_to("Video", tool_name, tool_name)