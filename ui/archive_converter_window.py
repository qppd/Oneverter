import customtkinter as ctk
from .base_window import BaseWindow
from converters.archive_converter import ArchiveConverterUI


class ArchiveConverterWindow(BaseWindow):
    """Window for the Archive Converter, inheriting from BaseWindow."""

    def __init__(self, parent):
        super().__init__(parent, title="Oneverter - Archive Converter", geometry="1024x768")
        self.resizable(True, True)
        self.minsize(800, 600)
        
        self.setup_ui()

    def setup_ui(self):
        """Setup the archive converter UI with a responsive layout."""
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Header
        header_frame = ctk.CTkFrame(self)
        header_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")

        # Back button - uses on_close from BaseWindow
        back_button = ctk.CTkButton(
            header_frame, text="← Back to Converters", command=self.on_close, width=150
        )
        back_button.pack(side="left")

        # Title
        title_label = ctk.CTkLabel(
            header_frame, text="📦 Archive Converter", font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(side="left", padx=20)

        # Create a content frame that will hold the specific converter's UI
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")

        # Instantiate the UI class, passing the content frame as the parent
        self.archive_ui = ArchiveConverterUI(content_frame) 