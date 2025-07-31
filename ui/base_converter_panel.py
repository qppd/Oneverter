import customtkinter as ctk
from .theme import Colors, Fonts, get_button_style, get_frame_style

class BaseConverterPanel(ctk.CTkFrame):
    """Base class for all converter panels."""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the base converter UI layout."""
        # Configure grid
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Header with title and description
        self.create_header()
        
        # Main content area
        self.content_frame = ctk.CTkFrame(self, **get_frame_style())
        self.content_frame.grid(row=1, column=0, sticky="nsew")
        
        # Setup the specific converter content
        self.setup_converter()
        
    def create_header(self):
        """Create the header with title and description."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        # Title
        self.title_label = ctk.CTkLabel(
            header,
            text=self.get_title(),
            font=Fonts.HEADING,
            text_color=Colors.TEXT
        )
        self.title_label.pack(side="left")
        
    def setup_converter(self):
        """
        Setup the specific converter UI.
        This should be overridden by subclasses.
        """
        pass
        
    def get_title(self) -> str:
        """
        Get the converter title.
        This should be overridden by subclasses.
        """
        return "Converter"
