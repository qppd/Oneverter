import customtkinter as ctk
from converters.audio_converter import AudioConverterUI
from ..base_converter_panel import BaseConverterPanel


class AudioConverterPanel(BaseConverterPanel):
    """Panel for the Audio Converter, for embedding in unified interface."""
    
    def get_title(self) -> str:
        """Get the panel title."""
        return "🎵 Audio Converter"
    
    def setup_converter(self):
        """Setup the specific converter UI."""
        self.audio_ui = AudioConverterUI(self.content_frame)