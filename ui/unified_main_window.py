import customtkinter as ctk
from typing import Dict, Any, Optional, Callable
from .theme import apply_theme, Colors, Fonts, get_button_style, get_frame_style
from .notifications import NotificationManager, ErrorDialog

# Import panel registry for dynamic panel loading
from .panels import PANEL_REGISTRY


class NavigationManager:
    """Manages navigation history and breadcrumbs for the unified interface."""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.history = []
        self.current_path = []
        
    def navigate_to(self, category: str, tool: str = None, title: str = None):
        """Navigate to a specific category or tool."""
        # Build navigation path
        new_path = [{"name": "Home", "category": None, "tool": None}]
        
        if category:
            new_path.append({"name": category, "category": category, "tool": None})
            
        if tool:
            display_title = title or tool
            new_path.append({"name": display_title, "category": category, "tool": tool})
            
        # Save current state to history if different
        if self.current_path != new_path:
            if self.current_path:
                self.history.append(self.current_path.copy())
            self.current_path = new_path
            
        self.main_window.update_breadcrumbs()
        
    def go_back(self):
        """Navigate back to previous location."""
        if self.history:
            self.current_path = self.history.pop()
            self.main_window.update_breadcrumbs()
            
            # Navigate to the previous location
            if len(self.current_path) == 1:  # Home
                self.main_window.show_home()
            elif len(self.current_path) == 2:  # Category
                category = self.current_path[1]["category"]
                self.main_window.show_category(category)
            else:  # Tool
                category = self.current_path[1]["category"]
                tool = self.current_path[2]["tool"]
                self.main_window.show_tool(category, tool)
                
    def get_breadcrumb_text(self) -> str:
        """Get formatted breadcrumb text."""
        return " > ".join([item["name"] for item in self.current_path])


class CategorySidebar(ctk.CTkFrame):
    """Collapsible sidebar with category navigation."""
    
    def __init__(self, parent, navigation_manager: NavigationManager):
        super().__init__(parent, **get_frame_style(), width=180)  # Fixed width for consistency
        self.navigation_manager = navigation_manager
        self.is_collapsed = False
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the sidebar UI."""
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Header with collapse button
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        
        self.collapse_button = ctk.CTkButton(
            header_frame, 
            text="☰", 
            width=30, 
            command=self.toggle_collapse,
            **get_button_style()
        )
        self.collapse_button.pack(side="left")
        
        self.sidebar_title = ctk.CTkLabel(
            header_frame, 
            text="Categories", 
            font=Fonts.HEADING,
            text_color=Colors.TEXT
        )
        self.sidebar_title.pack(side="left", padx=(10, 0))
        
        # Categories
        self.categories_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.categories_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        self.create_category_buttons()
        
    def create_category_buttons(self):
        """Create category navigation buttons."""
        categories = [
            {"icon": "🏠", "name": "Home", "category": None},
            {"icon": "📄", "name": "Document", "category": "Document"},
            {"icon": "🖼️", "name": "Image", "category": "Image"},
            {"icon": "🛠️", "name": "Video", "category": "Video"},
            {"icon": "🎵", "name": "Audio", "category": "Audio"},
            {"icon": "📦", "name": "Archive", "category": "Archive"},
            {"icon": "📊", "name": "Data", "category": "Data"},
        ]
        
        for i, category in enumerate(categories):
            btn = ctk.CTkButton(
                self.categories_frame,
                text=f"{category['icon']} {category['name']}",
                command=lambda cat=category['category']: self.navigate_to_category(cat),
                anchor="w",
                **get_button_style()
            )
            btn.grid(row=i, column=0, sticky="ew", pady=2)
            
    def navigate_to_category(self, category: str):
        """Navigate to a specific category."""
        if category is None:
            self.navigation_manager.navigate_to(None)
            self.navigation_manager.main_window.show_home()
        else:
            self.navigation_manager.navigate_to(category)
            self.navigation_manager.main_window.show_category(category)
            
    def toggle_collapse(self):
        """Toggle sidebar collapse state."""
        self.is_collapsed = not self.is_collapsed
        if self.is_collapsed:
            self.sidebar_title.pack_forget()
            self.categories_frame.grid_remove()
            self.collapse_button.configure(text="☰")
        else:
            self.sidebar_title.pack(side="left", padx=(10, 0))
            self.categories_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
            self.collapse_button.configure(text="✕")


class UnifiedMainWindow(ctk.CTkFrame):
    """Unified main window that contains all converter functionality."""
    
    def __init__(self, master, user_manager: Optional[Any] = None, logout_callback: Optional[Callable] = None):
        super().__init__(master)
        self.user_manager = user_manager
        self.logout_callback = logout_callback

        # Apply theme
        apply_theme()
        self.configure(fg_color=Colors.BACKGROUND)

        # Make the window resizable
        if isinstance(master, ctk.CTk):
            master.resizable(True, True)
            master.minsize(1000, 700)  # Minimum size for responsive design
            master.title("Oneverter - Unified Interface")

        # Initialize navigation
        self.navigation_manager = NavigationManager(self)

        # Notification manager for toasts
        self.notification_manager = NotificationManager(master)

        # Current content reference
        self.current_content = None

        self.setup_ui()
        self.show_home()
    def show_notification(self, message, type_="info", duration=3000):
        """Show a notification toast."""
        self.notification_manager.show_toast(message, type_, duration)

    def show_error(self, title, message, log_path=None):
        """Show a reusable error dialog."""
        ErrorDialog.show_error(self.master, title, message, log_path)
        
    def setup_ui(self):
        """Setup the unified interface layout."""
        # Configure main grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Sidebar
        self.sidebar = CategorySidebar(self, self.navigation_manager)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=(10, 10))
        
        # Main content area
        self.content_frame = ctk.CTkFrame(self, **get_frame_style())
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=(10, 10))
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        # Footer
        self.create_footer()
        
    def create_header(self):
        """Create the header with breadcrumbs and user info."""
        from ui.tooltip import Tooltip
        header_frame = ctk.CTkFrame(self, **get_frame_style())
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 5))

        # Back button
        self.back_button = ctk.CTkButton(
            header_frame,
            text="← Back",
            command=self.navigation_manager.go_back,
            width=80,
            **get_button_style()
        )
        self.back_button.pack(side="left", padx=10, pady=10)
        Tooltip(self.back_button, "Go back to previous screen")

        # Breadcrumbs
        self.breadcrumb_label = ctk.CTkLabel(
            header_frame,
            text="Home",
            font=Fonts.HEADING,
            text_color=Colors.TEXT
        )
        self.breadcrumb_label.pack(side="left", padx=(10, 0), pady=10)

        # User info and logout (right side)
        user_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        user_frame.pack(side="right", padx=10, pady=10)

        # Only show user info if user_manager is available
        if self.user_manager:
            user = self.user_manager.get_current_user()
            welcome_text = f"Welcome, {user['name']}!" if user else "Welcome!"
        else:
            welcome_text = "Oneverter"

        welcome_label = ctk.CTkLabel(
            user_frame, 
            text=welcome_text, 
            font=Fonts.BODY, 
            text_color=Colors.TEXT
        )
        welcome_label.pack(side="left", padx=(0, 10))

        # Only show logout button if logout_callback is available
        if self.logout_callback:
            logout_button = ctk.CTkButton(
                user_frame, 
                text="Logout", 
                command=self.logout_callback,
                width=80,
                **get_button_style("danger")
            )
            logout_button.pack(side="right")
            Tooltip(logout_button, "Log out and return to login screen")
        
    def create_footer(self):
        """Create the footer with status information."""
        from ui.tooltip import Tooltip
        footer_frame = ctk.CTkFrame(self, **get_frame_style())
        footer_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=(5, 10))

        # Status label
        self.status_label = ctk.CTkLabel(
            footer_frame,
            text="Ready",
            font=Fonts.SMALL,
            text_color=Colors.SUBTLE_TEXT
        )
        self.status_label.pack(side="left", padx=10, pady=5)
        Tooltip(self.status_label, "Current status of the application")

        # Copyright
        copyright_label = ctk.CTkLabel(
            footer_frame,
            text="© 2025 QPPD • Oneverter",
            font=Fonts.SMALL,
            text_color=Colors.SUBTLE_TEXT
        )
        copyright_label.pack(side="right", padx=10, pady=5)
        Tooltip(copyright_label, "Project copyright information")
        
    def update_breadcrumbs(self):
        """Update the breadcrumb display."""
        breadcrumb_text = self.navigation_manager.get_breadcrumb_text()
        self.breadcrumb_label.configure(text=breadcrumb_text)
        
        # Enable/disable back button
        can_go_back = len(self.navigation_manager.history) > 0
        self.back_button.configure(state="normal" if can_go_back else "disabled")
        
    def clear_content(self):
        """Clear the current content area."""
        if self.current_content:
            self.current_content.destroy()
            self.current_content = None
            
    def show_home(self):
        """Show the home screen with category selection."""
        self.clear_content()
        self.navigation_manager.navigate_to(None)
        
        # Create home content
        home_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        home_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        home_frame.grid_rowconfigure(1, weight=1)
        home_frame.grid_columnconfigure(0, weight=1)
        
        # Welcome section
        welcome_frame = ctk.CTkFrame(home_frame, fg_color="transparent")
        welcome_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        welcome_frame.grid_columnconfigure(0, weight=1)
        
        # Logo and title
        title_label = ctk.CTkLabel(
            welcome_frame,
            text="🚀 Oneverter",
            font=Fonts.TITLE,
            text_color=Colors.TEXT
        )
        title_label.grid(row=0, column=0, pady=(0, 10))
        
        subtitle_label = ctk.CTkLabel(
            welcome_frame,
            text="Your All-in-One Conversion Hub",
            font=Fonts.SUBTITLE,
            text_color=Colors.SUBTLE_TEXT
        )
        subtitle_label.grid(row=1, column=0)
        
        # Category grid
        categories_frame = ctk.CTkScrollableFrame(home_frame)
        categories_frame.grid(row=1, column=0, sticky="nsew")
        
        # Configure grid for responsive layout
        for i in range(3):
            categories_frame.grid_columnconfigure(i, weight=1)
            
        self.create_home_category_cards(categories_frame)
        self.current_content = home_frame
        
    def create_home_category_cards(self, parent):
        """Create category cards for the home screen."""
        categories = [
            {"icon": "📄", "title": "Document Converter", "desc": "Convert PDF, DOCX, TXT files", "category": "Document"},
            {"icon": "🖼️", "title": "Image Converter", "desc": "Convert, resize, compress images", "category": "Image"},
            {"icon": "🛠️", "title": "Video Tools", "desc": "Convert, trim, merge, and more", "category": "Video"},
            {"icon": "🎵", "title": "Audio Converter", "desc": "Convert formats, extract from video", "category": "Audio"},
            {"icon": "📦", "title": "Archive Converter", "desc": "Convert archives, extract files", "category": "Archive"},
            {"icon": "📊", "title": "Data Converter", "desc": "Convert CSV, Excel, JSON, XML", "category": "Data"},
        ]
        
        for i, category in enumerate(categories):
            row = i // 3
            col = i % 3
            self.create_category_card(
                parent, row, col,
                category["icon"], category["title"], category["desc"],
                lambda cat=category["category"]: self.show_category(cat)
            )
            
    def create_category_card(self, parent, row, col, icon, title, description, command):
        """Create a single category card."""
        card = ctk.CTkFrame(parent, **get_frame_style())
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        card.grid_rowconfigure(3, weight=1)
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
            text_color=Colors.SUBTLE_TEXT, wraplength=200
        )
        desc_label.grid(row=2, column=0, padx=10, pady=5)
        
        # Button
        button = ctk.CTkButton(card, text="Open Converter", command=command, **get_button_style())
        button.grid(row=3, column=0, padx=20, pady=20, sticky="s")
        
        # Make card clickable
        for widget in [card, icon_label, title_label, desc_label]:
            widget.bind("<Button-1>", lambda e, cmd=command: cmd())
            
    def show_category(self, category: str):
        """Show tools for a specific category."""
        self.clear_content()
        self.navigation_manager.navigate_to(category)
        
        # Create a frame to hold the converter content
        container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        # Create the appropriate converter panel based on category
        if category in PANEL_REGISTRY:
            panel_class = PANEL_REGISTRY[category]
            converter = panel_class(container)
        else:
            # Fallback for unknown categories
            converter = ctk.CTkFrame(container, fg_color="transparent")
            placeholder_label = ctk.CTkLabel(
                converter,
                text=f"Category {category} not implemented yet",
                font=Fonts.HEADING,
                text_color=Colors.TEXT
            )
            placeholder_label.pack(expand=True)
            
        converter.grid(row=0, column=0, sticky="nsew")
        self.current_content = container
        
    def create_tool_card(self, parent, row, col, icon, title, description, command):
        """Create a tool card similar to category cards but slightly smaller."""
        card = ctk.CTkFrame(parent, **get_frame_style())
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        card.grid_rowconfigure(3, weight=1)
        card.grid_columnconfigure(0, weight=1)
        
        # Icon
        icon_label = ctk.CTkLabel(card, text=icon, font=ctk.CTkFont(size=36))
        icon_label.grid(row=0, column=0, pady=(15, 5))
        
        # Title
        title_label = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=16, weight="bold"))
        title_label.grid(row=1, column=0, pady=5)
        
        # Description
        desc_label = ctk.CTkLabel(
            card, text=description, font=ctk.CTkFont(size=12),
            text_color=Colors.SUBTLE_TEXT, wraplength=180
        )
        desc_label.grid(row=2, column=0, padx=10, pady=5)
        
        # Button
        button = ctk.CTkButton(card, text="Open Tool", command=command, **get_button_style())
        button.grid(row=3, column=0, padx=15, pady=15, sticky="s")
        
        # Make card clickable
        for widget in [card, icon_label, title_label, desc_label]:
            widget.bind("<Button-1>", lambda e, cmd=command: cmd())
        
    def show_tool(self, category: str, tool: str):
        """Show a specific tool interface."""
        self.clear_content()
        self.navigation_manager.navigate_to(category, tool)
        
        # This will be implemented when we create the converter panels
        placeholder_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        placeholder_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        placeholder_label = ctk.CTkLabel(
            placeholder_frame,
            text=f"{tool} from {category} will be implemented here",
            font=Fonts.HEADING,
            text_color=Colors.TEXT
        )
        placeholder_label.pack(expand=True)
        
        self.current_content = placeholder_frame
        
    def update_status(self, message: str):
        """Update the status bar message."""
        self.status_label.configure(text=message)