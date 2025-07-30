import customtkinter as ctk
from PIL import Image
from customtkinter import CTkImage # Use CTkImage directly
import os

class AnimatedSpinner(ctk.CTkLabel):
    """A label that displays an animated GIF, compatible with CTkImage."""
    def __init__(self, parent, path_to_gif, size=(200, 200)):
        super().__init__(parent, text="")
        self.parent = parent
        self.path_to_gif = path_to_gif
        self.sequence_len = 0
        self.frames = []
        self.frame_index = 0
        self.delay = 100
        self.is_running = False
        self.size = size

        if os.path.exists(self.path_to_gif):
            self._load_gif()
        else:
            print(f"Error: GIF not found at {self.path_to_gif}")
            self.configure(text="⚠️") # Fallback text

    def _load_gif(self):
        """Load the GIF and extract its frames as CTkImage objects."""
        try:
            gif = Image.open(self.path_to_gif)
            self.sequence_len = gif.n_frames
            self.delay = gif.info.get('duration', 100)
            
            for i in range(self.sequence_len):
                gif.seek(i)
                # Create a CTkImage for each frame for HighDPI compatibility
                pil_frame = gif.copy()
                ctk_frame = CTkImage(light_image=pil_frame, size=self.size)
                self.frames.append(ctk_frame)
        except Exception as e:
            print(f"Error loading GIF: {e}")
            self.configure(text="⚠️")

    def _animate(self):
        """Cycle through the frames of the GIF."""
        if self.is_running and self.frames:
            self.frame_index = (self.frame_index + 1) % self.sequence_len
            self.configure(image=self.frames[self.frame_index])
            self.after(self.delay, self._animate)

    def start(self):
        """Start the animation."""
        if self.frames and not self.is_running:
            self.is_running = True
            self.frame_index = -1
            self._animate()
            
    def stop(self):
        """Stop the animation."""
        self.is_running = False

    def show(self):
        """Show the spinner and start animating."""
        self.start()
        # Ensure the spinner is on top of the overlay
        self.lift()
        self.place(relx=0.5, rely=0.5, anchor="center")
        
    def hide(self):
        """Stop animating and hide the spinner."""
        self.stop()
        self.place_forget() 