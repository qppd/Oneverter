import customtkinter as ctk

class Tooltip:
    """Simple tooltip for CustomTkinter widgets."""
    def __init__(self, widget, text, delay=500):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tipwindow = None
        self.id = None
        self.widget.bind("<Enter>", self.schedule)
        self.widget.bind("<FocusIn>", self.schedule)  # Show tooltip on keyboard focus
        self.widget.bind("<Leave>", self.hide)
        self.widget.bind("<FocusOut>", self.hide)
        self.widget.bind("<ButtonPress>", self.hide)

    def schedule(self, event=None):
        self.unschedule()
        self.id = self.widget.after(self.delay, self.show)

    def unschedule(self):
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None

    def show(self, event=None):
        if self.tipwindow or not self.text:
            return
        # Position tooltip near widget, but keep inside screen
        x, y, _, _ = self.widget.bbox("insert") if hasattr(self.widget, "bbox") else (0, 0, 0, 0)
        x += self.widget.winfo_rootx() + 20
        y += self.widget.winfo_rooty() + 20
        screen_width = self.widget.winfo_screenwidth()
        screen_height = self.widget.winfo_screenheight()
        width, height = 180, 40
        if x + width > screen_width:
            x = screen_width - width - 10
        if y + height > screen_height:
            y = screen_height - height - 10
        self.tipwindow = tw = ctk.CTkToplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = ctk.CTkLabel(tw, text=self.text, font=("Roboto", 11), fg_color="#333", text_color="#fff", corner_radius=6)
        label.pack(ipadx=8, ipady=4)

    def hide(self, event=None):
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None
