import customtkinter as ctk
from typing import Dict, Any, Optional, Callable
from abc import ABC, abstractmethod
from .theme import Colors, Fonts, get_button_style, get_frame_style, get_label_style
from .animated_spinner import AnimatedSpinner


class ConverterPanel(ctk.CTkFrame, ABC):
    """Base class for all converter panels in the unified interface."""
    
    def __init__(self, parent, category: str, tool_name: str, description: str = ""):
        super().__init__(parent, fg_color="transparent")
        self.category = category
        self.tool_name = tool_name
        self.description = description
        self.parent = parent
        
        # Configure grid
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Create common UI elements
        self.create_header()
        self.create_content_area()
        self.create_progress_area()
        
        # Initialize loading spinner
        self.loading_spinner = None
        self.init_loading_spinner()
        
        # Setup the specific converter UI
        self.setup_converter_ui()
        
    def create_header(self):
        """Create the standardized header for all converter panels."""
        header_frame = ctk.CTkFrame(self, **get_frame_style())
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Tool icon and title
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="w", padx=10, pady=10)
        
        # Get icon based on category
        icon = self.get_category_icon()
        
        title_label = ctk.CTkLabel(
            title_frame,
            text=f"{icon} {self.tool_name}",
            font=Fonts.HEADING,
            text_color=Colors.TEXT,
            wraplength=200,
            justify="center"
        )
        title_label.pack(side="left")
        
        # Description
        if self.description:
            desc_label = ctk.CTkLabel(
                header_frame,
                text=self.description,
                font=Fonts.BODY,
                text_color=Colors.SUBTLE_TEXT
            )
            desc_label.grid(row=0, column=1, sticky="w", padx=(20, 10), pady=10)
            
        # Quick actions (can be overridden by subclasses)
        self.quick_actions_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        self.quick_actions_frame.grid(row=0, column=2, sticky="e", padx=10, pady=10)
        
    def create_content_area(self):
        """Create the main content area where converter-specific UI goes."""
        self.content_frame = ctk.CTkScrollableFrame(self, **get_frame_style())
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.content_frame.grid_columnconfigure(0, weight=1)
        
    def create_progress_area(self):
        """Create the progress and status area."""
        self.progress_frame = ctk.CTkFrame(self, **get_frame_style())
        self.progress_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(5, 10))
        self.progress_frame.grid_columnconfigure(1, weight=1)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            self.progress_frame,
            text="Ready",
            font=Fonts.BODY,
            text_color=Colors.TEXT
        )
        self.status_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame)
        self.progress_bar.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.progress_bar.set(0)
        
        # Cancel button (initially hidden)
        self.cancel_button = ctk.CTkButton(
            self.progress_frame,
            text="Cancel",
            command=self.cancel_operation,
            width=80,
            **get_button_style("danger")
        )
        # Don't grid it initially - show only during operations
        
    def get_category_icon(self) -> str:
        """Get the icon for the current category."""
        icons = {
            "Document": "📄",
            "Image": "🖼️",
            "Video": "🛠️",
            "Audio": "🎵",
            "Archive": "📦",
            "Data": "📊"
        }
        return icons.get(self.category, "🔧")
        
    def init_loading_spinner(self):
        """Initialize the loading spinner."""
        try:
            self.loading_spinner = AnimatedSpinner(self, "assets/loading_spinner.gif")
        except Exception as e:
            print(f"Could not initialize loading spinner: {e}")
            self.loading_spinner = None
            
    def show_loading(self):
        """Show loading indicator."""
        if self.loading_spinner:
            self.loading_spinner.show()
        self.update_status("Processing...")
        self.show_cancel_button()
        
    def hide_loading(self):
        """Hide loading indicator."""
        if self.loading_spinner:
            self.loading_spinner.hide()
        self.hide_cancel_button()
        
    def show_cancel_button(self):
        """Show the cancel button during operations."""
        self.cancel_button.grid(row=0, column=2, padx=10, pady=10)
        
    def hide_cancel_button(self):
        """Hide the cancel button."""
        self.cancel_button.grid_remove()
        
    def update_status(self, message: str):
        """Update the status message."""
        self.status_label.configure(text=message)
        
    def update_progress(self, value: float):
        """Update the progress bar (0.0 to 1.0)."""
        self.progress_bar.set(value)
        
    def reset_progress(self):
        """Reset progress bar and status."""
        self.progress_bar.set(0)
        self.update_status("Ready")
        self.hide_loading()
        
    def add_quick_action(self, text: str, command: Callable, style: str = "default"):
        """Add a quick action button to the header."""
        button = ctk.CTkButton(
            self.quick_actions_frame,
            text=text,
            command=command,
            width=100,
            **get_button_style(style)
        )
        button.pack(side="right", padx=(5, 0))
        return button
        
    def create_section(self, title: str, parent=None) -> ctk.CTkFrame:
        """Create a standardized section with title."""
        if parent is None:
            parent = self.content_frame
            
        section_frame = ctk.CTkFrame(parent, **get_frame_style())
        section_frame.pack(fill="x", padx=10, pady=10)
        section_frame.grid_columnconfigure(0, weight=1)
        
        # Section title
        title_label = ctk.CTkLabel(
            section_frame,
            text=title,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=Colors.TEXT
        )
        title_label.pack(anchor="w", padx=15, pady=(15, 5))
        
        # Content area for the section
        content_area = ctk.CTkFrame(section_frame, fg_color="transparent")
        content_area.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        return content_area
        
    def create_file_selector(self, parent, title: str, filetypes: list, multiple: bool = False) -> Dict[str, Any]:
        """Create a standardized file selector widget."""
        selector_frame = ctk.CTkFrame(parent, fg_color="transparent")
        selector_frame.pack(fill="x", pady=5)
        selector_frame.grid_columnconfigure(1, weight=1)
        
        # Label
        label = ctk.CTkLabel(selector_frame, text=title, font=Fonts.BODY)
        label.grid(row=0, column=0, padx=(0, 10), sticky="w")
        
        # Entry (read-only)
        from tkinter import StringVar
        file_var = StringVar()
        entry = ctk.CTkEntry(
            selector_frame,
            textvariable=file_var,
            state="readonly",
            placeholder_text="No file selected"
        )
        entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        
        # Browse button
        def browse_files():
            from tkinter import filedialog
            if multiple:
                files = filedialog.askopenfilenames(filetypes=filetypes)
                if files:
                    file_var.set(f"{len(files)} files selected")
                    return files
            else:
                file = filedialog.askopenfilename(filetypes=filetypes)
                if file:
                    import os
                    file_var.set(os.path.basename(file))
                    return file
            return None
            
        browse_button = ctk.CTkButton(
            selector_frame,
            text="Browse",
            command=browse_files,
            width=80,
            **get_button_style()
        )
        browse_button.grid(row=0, column=2)
        
        return {
            "frame": selector_frame,
            "var": file_var,
            "entry": entry,
            "button": browse_button,
            "browse": browse_files
        }
        
    def create_option_menu(self, parent, title: str, values: list, default: str = None) -> Dict[str, Any]:
        """Create a standardized option menu."""
        option_frame = ctk.CTkFrame(parent, fg_color="transparent")
        option_frame.pack(fill="x", pady=5)
        
        # Label
        label = ctk.CTkLabel(option_frame, text=title, font=Fonts.BODY)
        label.pack(side="left", padx=(0, 10))
        
        # Option menu
        from tkinter import StringVar
        option_var = StringVar(value=default or values[0])
        option_menu = ctk.CTkOptionMenu(
            option_frame,
            variable=option_var,
            values=values
        )
        option_menu.pack(side="left")
        
        return {
            "frame": option_frame,
            "var": option_var,
            "menu": option_menu
        }
        
    def create_slider(self, parent, title: str, from_: float, to: float, default: float = None) -> Dict[str, Any]:
        """Create a standardized slider with label."""
        slider_frame = ctk.CTkFrame(parent, fg_color="transparent")
        slider_frame.pack(fill="x", pady=5)
        
        # Label
        label = ctk.CTkLabel(slider_frame, text=title, font=Fonts.BODY)
        label.pack(side="left", padx=(0, 10))
        
        # Slider
        from tkinter import DoubleVar
        slider_var = DoubleVar(value=default or from_)
        slider = ctk.CTkSlider(
            slider_frame,
            from_=from_,
            to=to,
            variable=slider_var
        )
        slider.pack(side="left", padx=(0, 10))
        
        # Value label
        value_label = ctk.CTkLabel(
            slider_frame,
            text=f"{slider_var.get():.1f}",
            font=Fonts.BODY,
            width=50
        )
        value_label.pack(side="left")
        
        # Update value label when slider changes
        def update_label(*args):
            value_label.configure(text=f"{slider_var.get():.1f}")
        slider_var.trace("w", update_label)
        
        return {
            "frame": slider_frame,
            "var": slider_var,
            "slider": slider,
            "label": value_label
        }
        
    def create_action_buttons(self, parent, buttons: list) -> Dict[str, ctk.CTkButton]:
        """Create a row of action buttons."""
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.pack(fill="x", pady=10)
        
        created_buttons = {}
        for button_config in buttons:
            btn = ctk.CTkButton(
                button_frame,
                text=button_config.get("text", "Button"),
                command=button_config.get("command", lambda: None),
                width=button_config.get("width", 120),
                **get_button_style(button_config.get("style", "default"))
            )
            btn.pack(side="left", padx=(0, 10))
            created_buttons[button_config.get("name", button_config["text"])] = btn
            
        return created_buttons
        
    @abstractmethod
    def setup_converter_ui(self):
        """Setup the converter-specific UI. Must be implemented by subclasses."""
        pass
        
    def cancel_operation(self):
        """Cancel the current operation. Can be overridden by subclasses."""
        self.reset_progress()
        self.update_status("Operation cancelled")
        
    def show_success_message(self, message: str):
        """Show a success message."""
        self.update_status(f"✅ {message}")
        
    def show_error_message(self, message: str):
        """Show an error message."""
        self.update_status(f"❌ {message}")
        
    def show_warning_message(self, message: str):
        """Show a warning message."""
        self.update_status(f"⚠️ {message}")


class TabConverterPanel(ConverterPanel):
    """Extended converter panel with tab support (like the audio converter)."""
    
    def __init__(self, parent, category: str, tool_name: str, description: str = ""):
        self.tabs = {}
        super().__init__(parent, category, tool_name, description)
        
    def setup_converter_ui(self):
        """Setup the tabbed interface."""
        # Create tab view
        self.tab_view = ctk.CTkTabview(self.content_frame)
        self.tab_view.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Setup tabs - to be implemented by subclasses
        self.setup_tabs()
        
    @abstractmethod
    def setup_tabs(self):
        """Setup the tabs for the converter. Must be implemented by subclasses."""
        pass
        
    def add_tab(self, name: str, title: str = None) -> ctk.CTkFrame:
        """Add a new tab and return its frame."""
        display_title = title or name
        tab_frame = self.tab_view.add(display_title)
        self.tabs[name] = tab_frame
        return tab_frame
        
    def get_tab(self, name: str) -> ctk.CTkFrame:
        """Get a tab frame by name."""
        return self.tabs.get(name)
        
    def switch_to_tab(self, name: str):
        """Switch to a specific tab."""
        if name in self.tabs:
            self.tab_view.set(name)


class GridConverterPanel(ConverterPanel):
    """Extended converter panel with grid-based tool selection (like video tools)."""
    
    def __init__(self, parent, category: str, tool_name: str, description: str = ""):
        self.tools = {}
        self.current_tool = None
        super().__init__(parent, category, tool_name, description)
        
    def setup_converter_ui(self):
        """Setup the grid-based tool selection."""
        # Create tools grid
        self.tools_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.tools_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configure grid
        for i in range(4):  # 4 columns
            self.tools_frame.grid_columnconfigure(i, weight=1)
            
        # Setup tools - to be implemented by subclasses
        self.setup_tools()
        
    @abstractmethod
    def setup_tools(self):
        """Setup the tools grid. Must be implemented by subclasses."""
        pass
        
    def add_tool_card(self, row: int, col: int, icon: str, title: str, description: str, command: Callable):
        """Add a tool card to the grid."""
        card = ctk.CTkFrame(self.tools_frame, **get_frame_style())
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # Card button
        card_button = ctk.CTkButton(
            card,
            text=f"{icon} {title}",
            command=command,
            anchor="w",
            **get_button_style()
        )
        card_button.pack(fill="x", padx=15, pady=(15, 5))
        
        # Description
        desc_label = ctk.CTkLabel(
            card,
            text=description,
            wraplength=200,
            justify="left",
            anchor="w",
            font=Fonts.BODY,
            text_color=Colors.SUBTLE_TEXT
        )
        desc_label.pack(fill="x", padx=15, pady=(0, 15))
        
        return card
        
    def show_tool_interface(self, tool_name: str, tool_ui_class):
        """Replace the tools grid with a specific tool interface."""
        # Clear current content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
        # Create tool interface
        self.current_tool = tool_ui_class(self.content_frame)
        self.current_tool.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add back button
        back_button = ctk.CTkButton(
            self.content_frame,
            text="← Back to Tools",
            command=self.show_tools_grid,
            width=120,
            **get_button_style()
        )
        back_button.pack(anchor="nw", padx=10, pady=10)
        
    def show_tools_grid(self):
        """Show the tools grid again."""
        # Clear current content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
        self.current_tool = None
        
        # Recreate tools grid
        self.setup_converter_ui()