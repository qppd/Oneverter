import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
from threading import Thread
import yt_dlp
from PIL import Image
from urllib.request import urlopen
import io

class YouTubeDownloaderUI:
    def __init__(self, parent):
        self.parent = parent
        self.info = None
        self.setup_ui()

    def setup_ui(self):
        self.parent.grid_rowconfigure(0, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)

        main_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)

        # URL Entry
        url_frame = ctk.CTkFrame(main_frame)
        url_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        url_frame.grid_columnconfigure(0, weight=1)
        
        self.url_entry = ctk.CTkEntry(url_frame, placeholder_text="Enter YouTube URL")
        self.url_entry.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        ctk.CTkButton(url_frame, text="Fetch Info", command=self.fetch_info).grid(row=0, column=1, padx=10, pady=10)

        # Video Info
        self.info_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        self.info_frame.grid(row=1, column=0, sticky="ew", pady=10)
        self.info_frame.grid_columnconfigure(1, weight=1)

        self.thumbnail_label = ctk.CTkLabel(self.info_frame, text="")
        self.thumbnail_label.grid(row=0, column=0, rowspan=3, padx=10, pady=10)
        self.title_label = ctk.CTkLabel(self.info_frame, text="Title: ", wraplength=400)
        self.title_label.grid(row=0, column=1, sticky="w", padx=10)
        self.duration_label = ctk.CTkLabel(self.info_frame, text="Duration: ")
        self.duration_label.grid(row=1, column=1, sticky="w", padx=10)

        # Download Options
        options_frame = ctk.CTkFrame(main_frame)
        options_frame.grid(row=2, column=0, sticky="ew", pady=10)
        options_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(options_frame, text="Download as:").grid(row=0, column=0, padx=10, pady=10)
        self.download_type_menu = ctk.CTkOptionMenu(options_frame, values=["Video (MP4)", "Video (WebM)", "Audio (MP3)"])
        self.download_type_menu.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        ctk.CTkButton(options_frame, text="Download", command=self.start_download_thread).grid(row=0, column=2, padx=10, pady=10)

        # Progress
        self.status_label = ctk.CTkLabel(main_frame, text="", anchor="w")
        self.status_label.grid(row=3, column=0, sticky="ew", padx=10, pady=10)

    def fetch_info(self):
        url = self.url_entry.get()
        if not url:
            return
        
        try:
            with yt_dlp.YoutubeDL() as ydl:
                self.info = ydl.extract_info(url, download=False)
                
            self.title_label.configure(text=f"Title: {self.info['title']}")
            self.duration_label.configure(text=f"Duration: {self.info['duration_string']}")
            
            # Load thumbnail
            thumbnail_url = self.info['thumbnail']
            with urlopen(thumbnail_url) as response:
                image_data = response.read()
            
            image = Image.open(io.BytesIO(image_data))
            self.thumbnail_image = ctk.CTkImage(light_image=image, dark_image=image, size=(160, 90))
            self.thumbnail_label.configure(image=self.thumbnail_image)

        except Exception as e:
            messagebox.showerror("Error", f"Could not fetch video info: {e}")

    def start_download_thread(self):
        thread = Thread(target=self.run_download)
        thread.start()

    def run_download(self):
        if not self.info:
            messagebox.showerror("Error", "Fetch video info before downloading.")
            return

        download_type = self.download_type_menu.get()
        output_path = filedialog.askdirectory(title="Select Download Location")

        if not output_path:
            return

        ydl_opts = {'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s')}
        
        if "Audio" in download_type:
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]
        else:
            # MP4 or WebM
            video_format = 'mp4' if 'MP4' in download_type else 'webm'
            ydl_opts['format'] = f'bestvideo[ext={video_format}]+bestaudio[ext=m4a]/best[ext={video_format}]/best'

        self.status_label.configure(text="Downloading...")

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.info['webpage_url']])
            self.status_label.configure(text="Download complete!")
            messagebox.showinfo("Success", "Download finished!")
        except Exception as e:
            self.status_label.configure(text=f"Error: {e}")
            messagebox.showerror("Error", f"Download failed: {e}") 