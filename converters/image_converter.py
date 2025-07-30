import customtkinter as ctk

class ImageConverterUI:
    """Placeholder UI for the Image Converter."""
    def __init__(self, parent_frame: ctk.CTkFrame):
        self.parent = parent_frame
        self._build_ui()

    def _build_ui(self):
        """Builds the placeholder UI inside the parent frame."""
        self.parent.grid_rowconfigure(0, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)

        content_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        content_frame.grid(row=0, column=0, sticky="nsew")
        
        content_frame.grid_rowconfigure((0, 3), weight=1)
        content_frame.grid_columnconfigure(0, weight=1)

        # Icon
        icon_label = ctk.CTkLabel(content_frame, text="🖼️", font=ctk.CTkFont(size=72))
        icon_label.grid(row=0, column=0, sticky="s", pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            content_frame, text="Image Converter", font=ctk.CTkFont(size=32, weight="bold")
        )
        title_label.grid(row=1, column=0, pady=10)
        
        # Message
        message_label = ctk.CTkLabel(
            content_frame,
            text="Coming Soon!\n\nFeatures:\n• Image format conversion (JPG ↔ PNG ↔ WEBP)\n• Image resizing and compression\n• Background removal using AI\n• Batch image processing",
            font=ctk.CTkFont(size=16),
            text_color="gray"
        )
        message_label.grid(row=2, column=0, pady=20) 