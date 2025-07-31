import customtkinter as ctk
from abc import ABC, abstractmethod


class BaseConverterUI(ABC):
    """Base class for all converter UIs. Provides common functionality and interface."""

    def __init__(self, parent_frame: ctk.CTkFrame):
        """Initialize the converter UI.
        
        Args:
            parent_frame: The parent frame where this UI will be built
        """
        self.parent = parent_frame
        self.input_files = []
        self.output_dir = ""
        self.tab_view = None
        self._setup_ui()
        self.build_ui()  # Call build_ui after setup

    def _setup_ui(self):
        """Setup the base UI structure. Child classes should override build_ui()."""
        # Configure parent frame
        if isinstance(self.parent, ctk.CTkFrame):
            self.parent.grid_rowconfigure(0, weight=1)
            self.parent.grid_columnconfigure(0, weight=1)
            
        # Create tab view if needed
        if self.has_tabs():
            self.tab_view = ctk.CTkTabview(self.parent)
            self.tab_view.pack(expand=True, fill="both", padx=10, pady=10)
            self.setup_tabs()

    def has_tabs(self) -> bool:
        """Override this method to return True if the converter uses tabs."""
        return False

    def setup_tabs(self):
        """Setup tabs for converters that use them. Override in child classes."""
        pass

    @abstractmethod
    def build_ui(self):
        """Build the converter-specific UI components.
        
        This method should be overridden by child classes to create their specific UI.
        """
        pass

    def browse_files(self):
        """Browse for input files. Should be implemented by child classes."""
        pass

    def clear_files(self):
        """Clear selected files. Should be implemented by child classes."""
        pass

    def update_file_list(self):
        """Update the file list display. Should be implemented by child classes."""
        pass

    def start_conversion(self):
        """Start the conversion process. Should be implemented by child classes."""
        pass