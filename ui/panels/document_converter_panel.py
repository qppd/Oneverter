import customtkinter as ctk
from converters.document_converter import DocumentConverterUI
from ..base_converter_panel import BaseConverterPanel


class DocumentConverterPanel(BaseConverterPanel):
    """Panel for the Document Converter, for embedding in unified interface."""
    
    def get_title(self) -> str:
        """Get the panel title."""
        return "📄 Document Converter"
    
    def setup_converter(self):
        """Setup the specific converter UI."""
        self.document_ui = DocumentConverterUI(self.content_frame)