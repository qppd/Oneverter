import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
from threading import Thread
from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip
from .base_converter import BaseConverter

class VideoAudioEditor(BaseConverter):
    def get_supported_formats(self):
        return [".mp4", ".avi", ".mov", ".mkv", ".webm"]

    def convert(self, input_path, output_path, options):
        try:
            video = VideoFileClip(input_path)
            
            action = options.get('action')
            
            if action == 'remove':
                final_video = video.without_audio()
            elif action == 'replace':
                audio_path = options.get('audio_path')
                if not audio_path:
                    raise ValueError("Audio file for replacement is required.")
                new_audio = AudioFileClip(audio_path)
                final_video = video.set_audio(new_audio)
            elif action == 'add':
                audio_path = options.get('audio_path')
                if not audio_path:
                    raise ValueError("Audio file to add is required.")
                new_audio = AudioFileClip(audio_path)
                original_audio = video.audio
                combined_audio = CompositeAudioClip([original_audio, new_audio])
                final_video = video.set_audio(combined_audio)
            else:
                raise ValueError("Invalid audio action specified.")
            
            final_video.write_videofile(output_path, codec='libx264')
            
            video.close()
            if 'new_audio' in locals():
                new_audio.close()
            final_video.close()
            
            return f"Successfully processed audio for {os.path.basename(input_path)}"

        except Exception as e:
            return f"Error processing audio: {e}"

class VideoAudioEditorUI:
    def __init__(self, parent):
        self.parent = parent
        self.video_path = None
        self.audio_path = None
        self.editor = VideoAudioEditor()
        self.setup_ui()

    def setup_ui(self):
        self.parent.grid_rowconfigure(0, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)

        main_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)

        # File Selection
        ctk.CTkButton(main_frame, text="Select Video", command=self.select_video).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.video_label = ctk.CTkLabel(main_frame, text="No video selected")
        self.video_label.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        # Audio Action
        self.action_var = ctk.StringVar(value="remove")
        action_frame = ctk.CTkFrame(main_frame)
        action_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=10)
        
        ctk.CTkRadioButton(action_frame, text="Remove Audio", variable=self.action_var, value="remove", command=self.toggle_audio_selection).pack(side="left", padx=10, pady=10)
        ctk.CTkRadioButton(action_frame, text="Replace Audio", variable=self.action_var, value="replace", command=self.toggle_audio_selection).pack(side="left", padx=10, pady=10)
        ctk.CTkRadioButton(action_frame, text="Add Audio", variable=self.action_var, value="add", command=self.toggle_audio_selection).pack(side="left", padx=10, pady=10)

        # Audio File Selection (for replace/add)
        self.audio_frame = ctk.CTkFrame(main_frame)
        self.audio_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=10)
        self.audio_select_button = ctk.CTkButton(self.audio_frame, text="Select Audio File", command=self.select_audio)
        self.audio_select_button.pack(side="left", padx=10, pady=10)
        self.audio_label = ctk.CTkLabel(self.audio_frame, text="No audio file selected")
        self.audio_label.pack(side="left", padx=10, pady=10)
        self.toggle_audio_selection()

        # --- Conversion ---
        conversion_frame = ctk.CTkFrame(main_frame)
        conversion_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        conversion_frame.grid_columnconfigure(0, weight=1)

        self.progress_bar = ctk.CTkProgressBar(conversion_frame)
        self.progress_bar.set(0)
        self.progress_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        ctk.CTkButton(conversion_frame, text="Process Audio", command=self.start_process_thread).grid(row=0, column=1, padx=10, pady=10)

        self.status_label = ctk.CTkLabel(main_frame, text="", anchor="w")
        self.status_label.grid(row=4, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
    
    def toggle_audio_selection(self):
        if self.action_var.get() in ["replace", "add"]:
            self.audio_select_button.configure(state="normal")
            self.audio_label.configure(state="normal")
        else:
            self.audio_select_button.configure(state="disabled")
            self.audio_label.configure(state="disabled")

    def select_video(self):
        path = filedialog.askopenfilename(title="Select Video File")
        if path:
            self.video_path = path
            self.video_label.configure(text=os.path.basename(path))

    def select_audio(self):
        path = filedialog.askopenfilename(title="Select Audio File")
        if path:
            self.audio_path = path
            self.audio_label.configure(text=os.path.basename(path))
            
    def start_process_thread(self):
        thread = Thread(target=self.run_process)
        thread.start()

    def run_process(self):
        if not self.video_path:
            messagebox.showerror("Error", "Please select a video file.")
            return

        action = self.action_var.get()
        if action in ["replace", "add"] and not self.audio_path:
            messagebox.showerror("Error", f"Please select an audio file to {action}.")
            return
            
        output_path = filedialog.asksaveasfilename(
            defaultextension=".mp4",
            title="Save Processed Video As..."
        )
        if not output_path:
            return

        options = {
            "action": action,
            "audio_path": self.audio_path
        }
        
        self.status_label.configure(text=f"Processing audio...")
        self.progress_bar.set(0.5)
        
        try:
            result = self.editor.convert(self.video_path, output_path, options)
            self.status_label.configure(text=result)
            messagebox.showinfo("Success", "Audio processed successfully!")
        except Exception as e:
            self.status_label.configure(text=f"Error: {e}")
            messagebox.showerror("Error", f"An error occurred: {e}")
            
        self.progress_bar.set(1)
        self.progress_bar.set(0) 