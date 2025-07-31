import customtkinter as ctk
from .base_converter_panel import BaseConverterPanel
from .theme import Colors, Fonts, get_button_style, get_frame_style

class DocumentConverterPanel(BaseConverterPanel):
    """Document converter panel with all document conversion tools."""
    
    def get_title(self) -> str:
        return "Document Converter"
        
    def setup_converter(self):
        """Setup the document converter interface."""
        # Configure content frame grid
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(1, weight=1)
        self.content_frame.grid_rowconfigure(3, weight=1)
        
        # Input file section
        self.create_input_section()
        
        # Conversion options
        self.create_conversion_options()
        
        # Output options
        self.create_output_section()
        
        # Progress and status
        self.create_progress_section()
        
    def create_input_section(self):
        """Create the input file selection section."""
        input_frame = ctk.CTkFrame(self.content_frame, **get_frame_style())
        input_frame.grid(row=0, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="ew")
        
        # Title
        ctk.CTkLabel(
            input_frame, 
            text="Input File",
            font=Fonts.SUBTITLE
        ).pack(anchor="w", padx=15, pady=(15, 5))
        
        # File selection
        file_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        file_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        self.file_path = ctk.CTkEntry(
            file_frame,
            placeholder_text="Select a document file...",
        )
        self.file_path.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        browse_btn = ctk.CTkButton(
            file_frame,
            text="Browse",
            width=100,
            **get_button_style()
        )
        browse_btn.pack(side="right")
        
    def create_conversion_options(self):
        """Create the conversion options section."""
        options_frame = ctk.CTkFrame(self.content_frame, **get_frame_style())
        options_frame.grid(row=1, column=0, padx=(20, 10), pady=(0, 20), sticky="nsew")
        
        # Title
        ctk.CTkLabel(
            options_frame,
            text="Conversion Options",
            font=Fonts.SUBTITLE
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
        # Format selection
        format_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        format_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        ctk.CTkLabel(
            format_frame,
            text="Output Format:",
            font=Fonts.BODY
        ).pack(side="left")
        
        self.format_var = ctk.StringVar(value="pdf")
        formats = ["pdf", "docx", "txt"]
        
        for fmt in formats:
            ctk.CTkRadioButton(
                format_frame,
                text=fmt.upper(),
                variable=self.format_var,
                value=fmt,
                font=Fonts.BODY
            ).pack(side="left", padx=10)
            
    def create_output_section(self):
        """Create the output options section."""
        output_frame = ctk.CTkFrame(self.content_frame, **get_frame_style())
        output_frame.grid(row=1, column=1, padx=(10, 20), pady=(0, 20), sticky="nsew")
        
        # Title
        ctk.CTkLabel(
            output_frame,
            text="Output Options",
            font=Fonts.SUBTITLE
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
        # Options
        options_frame = ctk.CTkFrame(output_frame, fg_color="transparent")
        options_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        self.compress_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            options_frame,
            text="Compress output file",
            variable=self.compress_var,
            font=Fonts.BODY
        ).pack(anchor="w", pady=5)
        
        self.open_after_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            options_frame,
            text="Open after conversion",
            variable=self.open_after_var,
            font=Fonts.BODY
        ).pack(anchor="w", pady=5)
        
    def create_progress_section(self):
        """Create the progress and status section."""
        progress_frame = ctk.CTkFrame(self.content_frame, **get_frame_style())
        progress_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="ew")
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(progress_frame)
        self.progress_bar.pack(fill="x", padx=15, pady=(15, 5))
        self.progress_bar.set(0)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            progress_frame,
            text="Ready",
            font=Fonts.BODY,
            text_color=Colors.SUBTLE_TEXT
        )
        self.status_label.pack(padx=15, pady=(0, 15))
        
        # Convert button
        self.convert_btn = ctk.CTkButton(
            progress_frame,
            text="Convert Document",
            **get_button_style()
        )
        self.convert_btn.pack(pady=(0, 15))
