
import customtkinter as ctk

# =================================================================================
# App Theme
# =================================================================================

# Color Palette (Nord-inspired)
class Colors:
    BACKGROUND = "#2E3440"       # Dark gray-blue
    FRAME = "#3B4252"            # Lighter gray-blue
    BUTTON = "#88C0D0"           # Frosty blue
    BUTTON_HOVER = "#81A1C1"     # Lighter frosty blue
    TEXT = "#ECEFF4"             # Off-white
    SUBTLE_TEXT = "#D8DEE9"      # Light gray
    ACCENT = "#BF616A"           # Muted red for accents/warnings
    SUCCESS = "#A3BE8C"          # Green for success messages
    BORDER = "#4C566A"           # Border color

# Font Styles
class Fonts:
    TITLE = ("Roboto", 32, "bold")
    SUBTITLE = ("Roboto", 16)
    HEADING = ("Roboto", 24, "bold")
    BUTTON = ("Roboto", 16, "bold")
    BODY = ("Roboto", 14)
    SMALL = ("Roboto", 12)

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

def get_button_style(variant="default"):
    """Returns a dictionary of styles for a CTkButton."""
    if variant == "danger":
        return {
            "fg_color": Colors.ACCENT,
            "hover_color": "#d08770" # Darker red on hover
        }
    return {
        "fg_color": Colors.BUTTON,
        "hover_color": Colors.BUTTON_HOVER,
        "text_color": Colors.BACKGROUND,
        "font": Fonts.BUTTON
    }

def get_frame_style():
    """Returns a dictionary of styles for a CTkFrame."""
    return {
        "fg_color": Colors.FRAME,
        "border_color": Colors.BORDER,
        "border_width": 1,
        "corner_radius": 10
    }

def get_label_style(variant="default"):
    """Returns a dictionary of styles for a CTkLabel."""
    if variant == "title":
        return {"font": Fonts.TITLE, "text_color": Colors.TEXT}
    if variant == "subtitle":
        return {"font": Fonts.SUBTITLE, "text_color": Colors.SUBTLE_TEXT}
    return {"font": Fonts.BODY, "text_color": Colors.TEXT} 