import customtkinter as ctk
from typing import List, Dict, Any
import pyautogui
import cv2
import numpy as np
from PIL import Image, ImageTk

class SourceItem:
    def __init__(self, name: str, source_type: str, settings: Dict[str, Any]):
        self.name = name
        self.source_type = source_type
        self.settings = settings
        self.active = True

class Scene:
    def __init__(self, name: str):
        self.name = name
        self.sources: List[SourceItem] = []

class ScreenRecorderPanel(ctk.CTkFrame):
    """Enhanced screen recorder panel with OBS-like features."""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.scenes: List[Scene] = [Scene("Scene 1")]
        self.current_scene = self.scenes[0]
        self.recording = False
        self.streaming = False
        self.setup_ui()

    def setup_ui(self):
        # Split into left panel (sources/scenes) and right panel (preview)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Left panel
        left_panel = ctk.CTkFrame(self)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Scenes
        scenes_frame = ctk.CTkFrame(left_panel)
        scenes_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(scenes_frame, text="Scenes", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        
        scenes_buttons = ctk.CTkFrame(scenes_frame)
        scenes_buttons.pack(fill="x", pady=2)
        
        ctk.CTkButton(scenes_buttons, text="+", width=30, command=self.add_scene).pack(side="left", padx=2)
        ctk.CTkButton(scenes_buttons, text="-", width=30, command=self.remove_scene).pack(side="left", padx=2)
        
        self.scenes_menu = ctk.CTkOptionMenu(scenes_frame, values=[scene.name for scene in self.scenes])
        self.scenes_menu.pack(fill="x", pady=2)

        # Sources
        sources_frame = ctk.CTkFrame(left_panel)
        sources_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(sources_frame, text="Sources", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        
        sources_buttons = ctk.CTkFrame(sources_frame)
        sources_buttons.pack(fill="x", pady=2)
        
        ctk.CTkButton(sources_buttons, text="+", width=30, command=self.add_source).pack(side="left", padx=2)
        ctk.CTkButton(sources_buttons, text="-", width=30, command=self.remove_source).pack(side="left", padx=2)
        
        self.sources_list = ctk.CTkTextbox(sources_frame, height=200)
        self.sources_list.pack(fill="x", pady=2)

        # Source properties
        properties_frame = ctk.CTkFrame(left_panel)
        properties_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(properties_frame, text="Properties", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        
        self.properties_container = ctk.CTkFrame(properties_frame)
        self.properties_container.pack(fill="x", pady=2)

        # Right panel (preview and controls)
        right_panel = ctk.CTkFrame(self)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        right_panel.grid_rowconfigure(0, weight=1)
        right_panel.grid_columnconfigure(0, weight=1)

        # Preview
        preview_frame = ctk.CTkFrame(right_panel)
        preview_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Stats overlay
        self.stats_var = ctk.StringVar(value="FPS: 0 | CPU: 0% | Memory: 0MB")
        stats_label = ctk.CTkLabel(preview_frame, textvariable=self.stats_var)
        stats_label.pack(anchor="nw", padx=5, pady=5)

        # Controls
        controls_frame = ctk.CTkFrame(right_panel)
        controls_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)

        # Recording controls
        rec_controls = ctk.CTkFrame(controls_frame)
        rec_controls.pack(side="left", fill="x", expand=True)
        
        self.rec_button = ctk.CTkButton(rec_controls, text="⚫ REC", command=self.toggle_recording)
        self.rec_button.pack(side="left", padx=5)
        
        self.stream_button = ctk.CTkButton(rec_controls, text="🔴 LIVE", command=self.toggle_streaming)
        self.stream_button.pack(side="left", padx=5)

        # Settings
        settings_frame = ctk.CTkFrame(controls_frame)
        settings_frame.pack(side="right")
        
        # Quality settings
        quality_frame = ctk.CTkFrame(settings_frame)
        quality_frame.pack(side="left", padx=5)
        
        ctk.CTkLabel(quality_frame, text="Quality:").pack(side="left", padx=2)
        self.quality_menu = ctk.CTkOptionMenu(quality_frame, values=["High", "Medium", "Low"])
        self.quality_menu.pack(side="left", padx=2)

        # Format settings
        format_frame = ctk.CTkFrame(settings_frame)
        format_frame.pack(side="left", padx=5)
        
        ctk.CTkLabel(format_frame, text="Format:").pack(side="left", padx=2)
        self.format_menu = ctk.CTkOptionMenu(format_frame, values=["MP4", "MKV", "AVI"])
        self.format_menu.pack(side="left", padx=2)

    def add_scene(self):
        """Add a new scene."""
        scene_num = len(self.scenes) + 1
        scene = Scene(f"Scene {scene_num}")
        self.scenes.append(scene)
        self.update_scenes_menu()

    def remove_scene(self):
        """Remove the current scene."""
        if len(self.scenes) > 1:
            self.scenes.remove(self.current_scene)
            self.current_scene = self.scenes[0]
            self.update_scenes_menu()

    def update_scenes_menu(self):
        """Update the scenes dropdown menu."""
        self.scenes_menu.configure(values=[scene.name for scene in self.scenes])

    def add_source(self):
        """Add a new source to the current scene."""
        add_source_window = SourceSelector(self)
        add_source_window.grab_set()

    def remove_source(self):
        """Remove the selected source from the current scene."""
        # Implementation for removing selected source
        pass

    def toggle_recording(self):
        """Toggle recording state."""
        self.recording = not self.recording
        if self.recording:
            self.rec_button.configure(text="⬛ STOP")
            # Start recording
        else:
            self.rec_button.configure(text="⚫ REC")
            # Stop recording

    def toggle_streaming(self):
        """Toggle streaming state."""
        self.streaming = not self.streaming
        if self.streaming:
            self.stream_button.configure(text="⬛ STOP")
            # Start streaming
        else:
            self.stream_button.configure(text="🔴 LIVE")
            # Stop streaming

class SourceSelector(ctk.CTkToplevel):
    """Dialog for adding new sources."""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Add Source")
        self.geometry("400x500")
        self.setup_ui()

    def setup_ui(self):
        # Source types
        sources = [
            ("Display Capture", "Capture entire screen or specific window"),
            ("Video Capture", "Webcam or other video input devices"),
            ("Audio Input", "Microphone or system audio"),
            ("Image", "Static image or slideshow"),
            ("Text", "Custom text overlay"),
            ("Browser", "Web page capture"),
            ("Color Source", "Solid color background"),
            ("Media Source", "Video or audio file playback")
        ]

        for source, description in sources:
            frame = ctk.CTkFrame(self)
            frame.pack(fill="x", padx=10, pady=5)
            
            ctk.CTkButton(frame, text=source, command=lambda s=source: self.add_source(s)).pack(anchor="w", padx=5, pady=2)
            ctk.CTkLabel(frame, text=description, text_color="gray").pack(anchor="w", padx=5, pady=2)

    def add_source(self, source_type: str):
        """Add the selected source type."""
        # Implementation for adding specific source type
        self.destroy()
