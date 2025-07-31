import customtkinter as ctk
from .base_window import BaseWindow
from .panels import (
    DocumentConverterPanel,
    ImageConverterPanel,
    VideoToolsPanel,
    AudioConverterPanel,
    ArchiveConverterPanel,
    DataConverterPanel
)


class ConverterWindow(BaseWindow):
    """Main converter window with category selection."""
    
    def __init__(self, parent):
        super().__init__(parent, title="Oneverter - Select Converter", geometry="1280x720")
        self.resizable(True, True)
        self.minsize(900, 700)

        self.setup_ui()
        self.current_panel = None

    def setup_ui(self):
        """Setup the main UI with a responsive grid layout."""
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Header (fixed at top)
        header_frame = ctk.CTkFrame(self)
        header_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        
        # Back button
        self.back_button = ctk.CTkButton(
            header_frame, text="← Back to Main", command=self.on_back, width=120
        )
        self.back_button.pack(side="left")
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame, text="Choose Your Converter", font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(side="left", padx=20)
        
        # Scrollable content area for category selection
        self.scrollable_frame = ctk.CTkScrollableFrame(self)
        self.scrollable_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")

        # Grid for category cards - make it responsive
        self.scrollable_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.create_converter_categories()
    
    def create_converter_categories(self):
        """Create converter category cards from a data structure."""
        categories = [
            {"icon": "📄", "title": "Document Converter", "desc": "Convert PDF, DOCX, TXT files", "panel": DocumentConverterPanel},
            {"icon": "🖼️", "title": "Image Converter", "desc": "Convert, resize, compress images", "panel": ImageConverterPanel},
            {"icon": "🛠️", "title": "Video Tools", "desc": "Convert, trim, merge, and more", "panel": VideoToolsPanel},
            {"icon": "🎵", "title": "Audio Converter", "desc": "Convert formats, extract from video", "panel": AudioConverterPanel},
            {"icon": "📦", "title": "Archive Converter", "desc": "Convert archives, extract files", "panel": ArchiveConverterPanel},
            {"icon": "📊", "title": "Data Converter", "desc": "Convert CSV, Excel, JSON, XML", "panel": DataConverterPanel},
        ]

        for i, category in enumerate(categories):
            row = i // 3
            col = i % 3
            self.create_category_card(
                self.scrollable_frame, row, col,
                category["icon"], category["title"], category["desc"],
                lambda p=category["panel"]: self.show_converter_panel(p)
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
        
        # Make card and its components clickable
        for widget in [card, icon_label, title_label, desc_label]:
            widget.bind("<Button-1>", lambda e, c=command: c())

    def show_converter_panel(self, panel_class):
        """Show a converter panel in the main content area."""
        # Hide category selection
        self.scrollable_frame.grid_remove()
        
        # Create and show the panel
        if self.current_panel:
            self.current_panel.destroy()
        
        self.current_panel = panel_class(self)
        self.current_panel.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        
        # Update back button
        self.back_button.configure(text="← Back to Categories", command=self.show_categories)

    def show_categories(self):
        """Show the category selection view."""
        if self.current_panel:
            self.current_panel.destroy()
            self.current_panel = None
        
        self.scrollable_frame.grid()
        self.back_button.configure(text="← Back to Main", command=self.on_close)

    def on_back(self):
        """Handle back button press."""
        if self.current_panel:
            self.show_categories()
        else:
            self.on_close()

    def show_converter_panel(self, panel_class):
        """Show a converter panel in the main content area."""
        # Clear existing content
        for widget in self.winfo_children():
            if widget != self.scrollable_frame:
                widget.destroy()

        # Create and show the panel
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        panel = panel_class(self)
        panel.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
            widget.bind("<Button-1>", lambda e, cmd=command: cmd()) 