import customtkinter as ctk

class BaseWindow(ctk.CTkToplevel):
    def __init__(self, parent=None, title="Oneverter", geometry="800x600"):
        if parent:
            super().__init__(parent)
            self.parent = parent
        else:
            # This logic is for the main window which has no parent
            super().__init__()

        self.title(title)
        self.geometry(geometry)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Center the window
        self.center_window()

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def on_close(self):
        """Handle window closing event."""
        if self.parent:
            self.parent.deiconify() # Show the parent window again
        self.destroy()

    def open_child_window(self, child_window_class):
        """Hide this window and open a new child window."""
        self.withdraw()
        child = child_window_class(self)
        child.grab_set()

# We need a main app class that is a CTk, not CTkToplevel
class BaseMainApp(ctk.CTk):
    def __init__(self, title="Oneverter", geometry="1024x768"):
        super().__init__()
        self.title(title)
        self.geometry(geometry)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Center the window
        self.center_window()
        
    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def on_close(self):
        self.destroy()

    def open_toplevel_window(self, child_window_class):
        """Hide the main window and open a new toplevel window."""
        self.withdraw()
        child = child_window_class(self)
        child.grab_set() 