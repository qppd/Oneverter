import customtkinter as ctk

class ModernConverterUI:
    """Base class for modern-style converter interfaces."""
    
    def __init__(self, parent_frame: ctk.CTkFrame):
        self.parent = parent_frame
        self.build_ui()
    
    def build_ui(self):
        """Build the modern UI."""
        self.main_frame = ctk.CTkFrame(self.parent)
        self.main_frame.pack(fill="both", expand=True)
