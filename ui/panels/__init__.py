"""
Converter panels for the unified Oneverter interface.

This package contains all the converter panels that replace the old window-based architecture.
Each panel inherits from ConverterPanel and provides a consistent interface within the main window.
"""

from .audio_converter_panel import AudioConverterPanel
from .video_tools_panel import VideoToolsPanel
from .document_converter_panel import DocumentConverterPanel
from .image_converter_panel import ImageConverterPanel
from .archive_converter_panel import ArchiveConverterPanel
from .data_converter_panel import DataConverterPanel

__all__ = [
    'AudioConverterPanel',
    'VideoToolsPanel', 
    'DocumentConverterPanel',
    'ImageConverterPanel',
    'ArchiveConverterPanel',
    'DataConverterPanel'
]

# Panel registry for easy lookup
PANEL_REGISTRY = {
    'Audio': AudioConverterPanel,
    'Video': VideoToolsPanel,
    'Document': DocumentConverterPanel,
    'Image': ImageConverterPanel,
    'Archive': ArchiveConverterPanel,
    'Data': DataConverterPanel
}

def get_panel_class(category: str):
    """Get the panel class for a given category."""
    return PANEL_REGISTRY.get(category)