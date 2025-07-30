import customtkinter as ctk
from .base_window import BaseWindow
from .document_converter_window import DocumentConverterWindow
from .image_converter_window import ImageConverterWindow
from .video_converter_window import VideoConverterWindow
from .audio_converter_window import AudioConverterWindow
from .archive_converter_window import ArchiveConverterWindow
from .data_converter_window import DataConverterWindow


class ConverterWindow(BaseWindow):
    """Main converter window with category selection."""
    
    def __init__(self, parent):
        super().__init__(parent, title="Oneverter - Select Converter", geometry="1280x720")
        self.resizable(True, True)
        self.minsize(900, 700)

        self.setup_ui()

    def setup_ui(self):
        """Setup the main UI with a responsive grid layout."""
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Header (fixed at top)
        header_frame = ctk.CTkFrame(self)
        header_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        
        # Back button
        self.back_button = ctk.CTkButton(
            header_frame, text="← Back to Main", command=self.on_close, width=120
        )
        self.back_button.pack(side="left")
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame, text="Choose Your Converter", font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(side="left", padx=20)
        
        # Scrollable content area
        self.scrollable_frame = ctk.CTkScrollableFrame(self)
        self.scrollable_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")

        # Grid for category cards - make it responsive
        self.scrollable_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.create_converter_categories()
    
    def create_converter_categories(self):
        """Create converter category cards from a data structure."""
        categories = [
            {"icon": "📄", "title": "Document Converter", "desc": "Convert PDF, DOCX, TXT files", "window": DocumentConverterWindow},
            {"icon": "🖼️", "title": "Image Converter", "desc": "Convert, resize, compress images", "window": ImageConverterWindow},
            {"icon": "🎥", "title": "Video Converter", "desc": "Convert video formats, extract frames", "window": VideoConverterWindow},
            {"icon": "🎵", "title": "Audio Converter", "desc": "Convert formats, extract from video", "window": AudioConverterWindow},
            {"icon": "📦", "title": "Archive Converter", "desc": "Convert archives, extract files", "window": ArchiveConverterWindow},
            {"icon": "📊", "title": "Data Converter", "desc": "Convert CSV, Excel, JSON, XML", "window": DataConverterWindow},
        ]

        for i, category in enumerate(categories):
            row = i // 3
            col = i % 3
            self.create_category_card(
                self.scrollable_frame, row, col,
                category["icon"], category["title"], category["desc"],
                lambda w=category["window"]: self.open_child_window(w)
            )
    
    def create_category_card(self, parent, row, col, icon, title, description, command):
        """Create a single, clickable category card."""
        card = ctk.CTkFrame(parent, corner_radius=10)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        card.grid_rowconfigure(3, weight=1) # Push button to bottom
        card.grid_columnconfigure(0, weight=1)

        # Icon
        icon_label = ctk.CTkLabel(card, text=icon, font=ctk.CTkFont(size=48))
        icon_label.grid(row=0, column=0, pady=(20, 10))
        
        # Title
        title_label = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=18, weight="bold"))
        title_label.grid(row=1, column=0, pady=5)
        
        # Description
        desc_label = ctk.CTkLabel(
            card, text=description, font=ctk.CTkFont(size=12),
            text_color="gray", wraplength=200
        )
        desc_label.grid(row=2, column=0, padx=10, pady=5)
        
        # Button
        button = ctk.CTkButton(card, text="Open Converter", command=command)
        button.grid(row=3, column=0, padx=20, pady=20, sticky="s")
        
        # Make the entire card clickable
        for widget in [card, icon_label, title_label, desc_label]:
            widget.bind("<Button-1>", lambda e, cmd=command: cmd()) 