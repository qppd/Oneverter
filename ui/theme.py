
import customtkinter as ctk

# =================================================================================
# App Theme
# =================================================================================

# Color Palette (Modern Dark Theme - inspired by Material Design Dark)
class Colors:
    BACKGROUND = "#121212"       # Deep dark gray
    SURFACE = "#1E1E1E"           # Card/surface color
    FRAME = "#2D2D2D"             # Frame background
    PRIMARY = "#BB86FC"           # Purple primary
    PRIMARY_VARIANT = "#3700B3"   # Darker purple
    SECONDARY = "#03DAC6"         # Teal secondary
    ERROR = "#CF6679"             # Red error
    ON_PRIMARY = "#000000"        # Text on primary
    ON_BACKGROUND = "#FFFFFF"     # Text on background
    ON_SURFACE = "#FFFFFF"        # Text on surface
    TEXT = "#E0E0E0"              # Primary text
    SUBTLE_TEXT = "#B0B0B0"       # Secondary text
    BORDER = "#424242"            # Border color
    SUCCESS = "#4CAF50"           # Green success
    WARNING = "#FF9800"           # Orange warning
    ACCENT = "#FF5722"            # Accent color

# Font Styles (Modern Typography - Compact)
class Fonts:
    TITLE = ("Inter", 20, "bold")      # App title - reduced
    SUBTITLE = ("Inter", 14)           # Section subtitles - reduced
    HEADING = ("Inter", 16, "bold")    # Panel headings - reduced
    SUBHEADING = ("Inter", 12, "bold") # Sub headings - reduced
    BODY = ("Inter", 11)               # Body text - reduced
    BUTTON = ("Inter", 11, "bold")     # Button text - reduced
    SMALL = ("Inter", 10)              # Small text/captions - reduced
    CAPTION = ("Inter", 9)             # Captions - reduced

# Global Widget Styling
def apply_theme():
    """Sets the global appearance and theme for the application."""
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue") # Keep base theme for some defaults

    # You can override specific theme colors here if needed,
    # but CustomTkinter's theme handling is quite good.
    # For deeper customization, you might edit the theme JSON file.

# =================================================================================
# Shared UI Component Styles
# =================================================================================

def get_button_style(variant="default", size="default"):
    """Returns a dictionary of styles for a CTkButton."""
    base_style = {
        "text_color": Colors.ON_PRIMARY,
        "font": Fonts.BUTTON,
        "corner_radius": 8
    }
    
    if size == "large":
        base_style["height"] = 36  # Reduced from 48
    elif size == "small":
        base_style["height"] = 28  # Reduced from 32
        base_style["font"] = Fonts.SMALL
    else:
        base_style["height"] = 32  # Reduced from 40
    
    if variant == "danger":
        base_style.update({
            "fg_color": Colors.ERROR,
            "hover_color": "#E57373"
        })
    elif variant == "success":
        base_style.update({
            "fg_color": Colors.SUCCESS,
            "hover_color": "#66BB6A"
        })
    elif variant == "secondary":
        base_style.update({
            "fg_color": Colors.SECONDARY,
            "hover_color": "#00BFA5",
            "text_color": Colors.BACKGROUND
        })
    else:  # primary
        base_style.update({
            "fg_color": Colors.PRIMARY,
            "hover_color": "#9C64D9"
        })
    
    return base_style

def get_frame_style(elevation="default"):
    """Returns a dictionary of styles for a CTkFrame."""
    if elevation == "card":
        return {
            "fg_color": Colors.SURFACE,
            "border_color": Colors.BORDER,
            "border_width": 1,
            "corner_radius": 16
        }
    return {
        "fg_color": Colors.FRAME,
        "border_color": Colors.BORDER,
        "border_width": 1,
        "corner_radius": 12
    }

def get_label_style(variant="default"):
    """Returns a dictionary of styles for a CTkLabel."""
    styles = {
        "title": {"font": Fonts.TITLE, "text_color": Colors.TEXT},
        "heading": {"font": Fonts.HEADING, "text_color": Colors.TEXT},
        "subheading": {"font": Fonts.SUBHEADING, "text_color": Colors.TEXT},
        "subtitle": {"font": Fonts.SUBTITLE, "text_color": Colors.SUBTLE_TEXT},
        "caption": {"font": Fonts.CAPTION, "text_color": Colors.SUBTLE_TEXT},
        "body": {"font": Fonts.BODY, "text_color": Colors.TEXT},
        "default": {"font": Fonts.BODY, "text_color": Colors.TEXT}
    }
    return styles.get(variant, styles["default"]) 