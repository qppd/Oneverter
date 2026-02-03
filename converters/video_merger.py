import customtkinter as ctk
from tkinter import filedialog, messagebox, dnd
import os
from threading import Thread
from moviepy import VideoFileClip, concatenate_videoclips, vfx
from .base_converter import BaseConverter
import tkinter as tk

class VideoMerger(BaseConverter):
    def get_supported_formats(self):
        return [".mp4", ".avi", ".mov", ".mkv", ".webm"]

    def convert(self, input_paths, output_path, options):
        try:
            clips = [VideoFileClip(path) for path in input_paths]
            
            if options.get('fade_transition'):
                # Add fade-in and fade-out to each clip to simulate a crossfade
                clips = [clip.fx(vfx.fadein, 0.5).fx(vfx.fadeout, 0.5) for clip in clips]

            final_clip = concatenate_videoclips(clips, method="compose")
            final_clip.write_videofile(output_path, codec='libx264')
            
            for clip in clips:
                clip.close()
            final_clip.close()

            return f"Successfully merged {len(input_paths)} videos."

        except Exception as e:
            return f"Error merging videos: {e}"

class VideoMergerUI:
    def __init__(self, parent):
        self.parent = parent
        self.files = []
        self.merger = VideoMerger()
        self.setup_ui()

    def setup_ui(self):
        self.parent.grid_rowconfigure(0, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)

        main_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        
        # --- File Selection ---
        file_frame = ctk.CTkFrame(main_frame)
        file_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        ctk.CTkButton(file_frame, text="Add Videos", command=self.add_files).pack(side="left", padx=10, pady=10)
        ctk.CTkButton(file_frame, text="Clear", command=self.clear_files).pack(side="left", padx=10, pady=10)

        # --- File List (with drag-and-drop) ---
        self.listbox = tk.Listbox(main_frame, selectmode=tk.SINGLE)
        self.listbox.grid(row=1, column=0, sticky="nsew", pady=10)
        self.listbox.bind("<B1-Motion>", self.drag)
        self.listbox.bind("<ButtonRelease-1>", self.drop)
        
        # --- Settings ---
        settings_frame = ctk.CTkFrame(main_frame)
        settings_frame.grid(row=2, column=0, sticky="ew", pady=10)
        self.fade_var = ctk.BooleanVar()
        ctk.CTkCheckBox(settings_frame, text="Add fade transition between clips", variable=self.fade_var).pack(side="left", padx=10, pady=10)
        
        # --- Conversion ---
        conversion_frame = ctk.CTkFrame(main_frame)
        conversion_frame.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        conversion_frame.grid_columnconfigure(0, weight=1)

        self.progress_bar = ctk.CTkProgressBar(conversion_frame)
        self.progress_bar.set(0)
        self.progress_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        ctk.CTkButton(conversion_frame, text="Merge", command=self.start_merge_thread).grid(row=0, column=1, padx=10, pady=10)

        self.status_label = ctk.CTkLabel(main_frame, text="", anchor="w")
        self.status_label.grid(row=4, column=0, sticky="ew", padx=10, pady=10)
        
    def add_files(self):
        new_files = filedialog.askopenfilenames(
            title="Select Video Files to Merge",
            filetypes=[("Video Files", "*.mp4 *.avi *.mov *.mkv *.webm"), ("All files", "*.*")]
        )
        if new_files:
            for file_path in new_files:
                self.files.append(file_path)
                self.listbox.insert(tk.END, os.path.basename(file_path))

    def clear_files(self):
        self.files = []
        self.listbox.delete(0, tk.END)

    def drag(self, event):
        self.drag_index = self.listbox.nearest(event.y)

    def drop(self, event):
        drop_index = self.listbox.nearest(event.y)
        if self.drag_index is not None and self.drag_index != drop_index:
            item = self.files.pop(self.drag_index)
            self.files.insert(drop_index, item)
            
            # Update listbox
            self.listbox.delete(0, tk.END)
            for file_path in self.files:
                self.listbox.insert(tk.END, os.path.basename(file_path))
        self.drag_index = None

    def start_merge_thread(self):
        thread = Thread(target=self.run_merge)
        thread.start()

    def run_merge(self):
        if len(self.files) < 2:
            messagebox.showerror("Error", "Please select at least two videos to merge.")
            return

        output_path = filedialog.asksaveasfilename(
            defaultextension=".mp4",
            filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")],
            title="Save Merged Video As..."
        )
        if not output_path:
            return

        options = {"fade_transition": self.fade_var.get()}
        
        self.status_label.configure(text="Merging videos...")
        self.progress_bar.set(0.5)

        try:
            result = self.merger.convert(self.files, output_path, options)
            self.status_label.configure(text=result)
            messagebox.showinfo("Success", "Videos merged successfully!")
        except Exception as e:
            self.status_label.configure(text=f"Error: {e}")
            messagebox.showerror("Error", f"An error occurred: {e}")
        
        self.progress_bar.set(1)
        self.progress_bar.set(0) 