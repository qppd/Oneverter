import customtkinter as ctk
from converters.image_converter import ImageConverterUI
from ..base_converter_panel import BaseConverterPanel


class ImageConverterPanel(BaseConverterPanel):
    """Panel for the Image Converter, for embedding in unified interface."""
    
    def get_title(self) -> str:
        """Get the panel title."""
        return "🖼️ Image Converter"
    
    def setup_converter(self):
        """Setup the specific converter UI."""
        self.image_ui = ImageConverterUI(self.content_frame)