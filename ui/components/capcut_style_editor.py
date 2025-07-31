import customtkinter as ctk
from typing import List, Dict, Any, Optional
from PIL import Image, ImageTk
import cv2
import numpy as np

class CapcutTimelineClip(ctk.CTkFrame):
    """Represents a clip in the timeline, similar to CapCut's style."""
    
    def __init__(self, parent, thumbnail: Optional[Image.Image] = None, duration: float = 0.0):
        super().__init__(parent)
        self.thumbnail = thumbnail
        self.duration = duration
        self.selected = False
        self.setup_ui()
        
    def setup_ui(self):
        self.configure(fg_color="#2B2B2B", corner_radius=4)
        
        # Thumbnail display
        if self.thumbnail:
            # Convert PIL image to CTk image
            self.thumb_label = ctk.CTkLabel(self, text="")
            self.thumb_label.pack(fill="both", expand=True)
            
        # Duration label
        self.duration_label = ctk.CTkLabel(
            self, 
            text=f"{self.duration:.1f}s",
            font=("Arial", 10),
            fg_color="#1E1E1E",
            corner_radius=2
        )
        self.duration_label.pack(side="bottom", pady=2)
        
    def set_selected(self, selected: bool):
        self.selected = selected
        self.configure(fg_color="#3B3B3B" if selected else "#2B2B2B")

class CapcutTimeline(ctk.CTkFrame):
    """CapCut-style timeline with real-time preview."""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.clips: List[CapcutTimelineClip] = []
        self.current_time = 0.0
        self.scale = 100  # pixels per second
        self.setup_ui()
        
    def setup_ui(self):
        self.configure(fg_color="#1B1B1B")
        
        # Timeline header
        self.header = ctk.CTkFrame(self, fg_color="#1B1B1B", height=30)
        self.header.pack(fill="x")
        
        # Timestamp markers
        self.timestamp_canvas = ctk.CTkCanvas(
            self.header,
            bg="#1B1B1B",
            highlightthickness=0,
            height=20
        )
        self.timestamp_canvas.pack(fill="x")
        
        # Tracks container
        self.tracks_frame = ctk.CTkFrame(self, fg_color="#1B1B1B")
        self.tracks_frame.pack(fill="both", expand=True)
        
        # Playhead
        self.playhead = ctk.CTkFrame(self, fg_color="#FF5252", width=2)
        
        self.update_timestamps()
        
    def update_timestamps(self):
        """Update timestamp markers."""
        self.timestamp_canvas.delete("all")
        width = self.timestamp_canvas.winfo_width()
        
        # Draw major and minor ticks
        for x in range(0, width, int(self.scale)):
            time = x / self.scale
            if time % 1 == 0:  # Major tick (seconds)
                self.timestamp_canvas.create_line(
                    x, 15, x, 20,
                    fill="#FFFFFF"
                )
                self.timestamp_canvas.create_text(
                    x, 10,
                    text=f"{int(time)}s",
                    fill="#FFFFFF",
                    font=("Arial", 8)
                )
            else:  # Minor tick
                self.timestamp_canvas.create_line(
                    x, 18, x, 20,
                    fill="#666666"
                )

class CapcutToolbar(ctk.CTkFrame):
    """CapCut-style toolbar with editing tools."""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        self.configure(fg_color="#2B2B2B")
        
        # Tool categories
        categories = [
            ("✂️ Split", self.split_clip),
            ("🔄 Speed", self.adjust_speed),
            ("🎵 Audio", self.edit_audio),
            ("📝 Text", self.add_text),
            ("🎨 Effects", self.add_effect),
            ("🎭 Transitions", self.add_transition),
            ("🖼️ Filters", self.add_filter),
            ("⭐ Stickers", self.add_sticker)
        ]
        
        for label, command in categories:
            btn = ctk.CTkButton(
                self,
                text=label,
                command=command,
                width=80,
                height=60,
                corner_radius=8,
                fg_color="#3B3B3B",
                hover_color="#4B4B4B"
            )
            btn.pack(side="left", padx=5, pady=10)
            
    def split_clip(self): pass
    def adjust_speed(self): pass
    def edit_audio(self): pass
    def add_text(self): pass
    def add_effect(self): pass
    def add_transition(self): pass
    def add_filter(self): pass
    def add_sticker(self): pass

class CapcutPreview(ctk.CTkFrame):
    """Video preview window with CapCut-style controls."""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.playing = False
        self.setup_ui()
        
    def setup_ui(self):
        self.configure(fg_color="#1B1B1B")
        
        # Preview canvas
        self.preview_frame = ctk.CTkFrame(
            self,
            fg_color="#000000",
            corner_radius=0
        )
        self.preview_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Control bar
        controls = ctk.CTkFrame(self, fg_color="#2B2B2B", height=40)
        controls.pack(fill="x", padx=20, pady=(0, 20))
        
        # Playback controls
        btn_frame = ctk.CTkFrame(controls, fg_color="transparent")
        btn_frame.pack(side="left", padx=10)
        
        self.play_btn = ctk.CTkButton(
            btn_frame,
            text="▶",
            width=40,
            height=30,
            command=self.toggle_play
        )
        self.play_btn.pack(side="left", padx=2)
        
        # Time display
        self.time_label = ctk.CTkLabel(
            controls,
            text="00:00 / 00:00",
            font=("Arial", 12)
        )
        self.time_label.pack(side="right", padx=10)
        
    def toggle_play(self):
        self.playing = not self.playing
        self.play_btn.configure(text="⏸" if self.playing else "▶")

class CapcutSidebar(ctk.CTkFrame):
    """CapCut-style sidebar with media and effects libraries."""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        self.configure(fg_color="#2B2B2B", width=300)
        
        # Tabs
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.pack(fill="both", expand=True)
        
        # Media tab
        media_tab = self.tab_view.add("Media")
        self.setup_media_tab(media_tab)
        
        # Effects tab
        effects_tab = self.tab_view.add("Effects")
        self.setup_effects_tab(effects_tab)
        
        # Audio tab
        audio_tab = self.tab_view.add("Audio")
        self.setup_audio_tab(audio_tab)
        
    def setup_media_tab(self, tab):
        # Media browser
        browse_btn = ctk.CTkButton(
            tab,
            text="Import Media",
            height=40,
            fg_color="#3B3B3B"
        )
        browse_btn.pack(fill="x", padx=10, pady=10)
        
        # Media list
        self.media_list = ctk.CTkScrollableFrame(tab)
        self.media_list.pack(fill="both", expand=True, padx=10, pady=10)
        
    def setup_effects_tab(self, tab):
        categories = [
            "Popular Effects",
            "Basic",
            "Filters",
            "Animations",
            "Transitions",
            "Split Screen",
            "Masks"
        ]
        
        for category in categories:
            frame = ctk.CTkFrame(tab, fg_color="#3B3B3B")
            frame.pack(fill="x", padx=10, pady=5)
            
            label = ctk.CTkLabel(
                frame,
                text=category,
                font=("Arial", 12, "bold")
            )
            label.pack(anchor="w", padx=10, pady=10)
            
    def setup_audio_tab(self, tab):
        categories = [
            "Sound Effects",
            "Music",
            "Voice Recording",
            "Background Sounds"
        ]
        
        for category in categories:
            frame = ctk.CTkFrame(tab, fg_color="#3B3B3B")
            frame.pack(fill="x", padx=10, pady=5)
            
            label = ctk.CTkLabel(
                frame,
                text=category,
                font=("Arial", 12, "bold")
            )
            label.pack(anchor="w", padx=10, pady=10)

class CapcutStyleEditor(ctk.CTkFrame):
    """Main CapCut-style video editor interface."""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        self.configure(fg_color="#1B1B1B")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Toolbar at top
        self.toolbar = CapcutToolbar(self)
        self.toolbar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        # Sidebar on left
        self.sidebar = CapcutSidebar(self)
        self.sidebar.grid(row=1, column=0, sticky="ns", padx=10, pady=5)
        
        # Main content area
        content = ctk.CTkFrame(self, fg_color="#1B1B1B")
        content.grid(row=1, column=1, sticky="nsew", padx=10, pady=5)
        content.grid_rowconfigure(0, weight=1)
        content.grid_columnconfigure(0, weight=1)
        
        # Preview area
        self.preview = CapcutPreview(content)
        self.preview.pack(fill="both", expand=True)
        
        # Timeline at bottom
        self.timeline = CapcutTimeline(content)
        self.timeline.configure(height=200)  # Set height using configure
        self.timeline.pack(fill="x", pady=(10, 0))
