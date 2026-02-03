import customtkinter as ctk
from tkinter import filedialog, Listbox, Scrollbar, MULTIPLE, messagebox
from .base_converter import BaseConverter
from .base_converter_ui import BaseConverterUI
from pydub import AudioSegment
import os
import threading
import wave
import pyaudio  # You may need to install this package
from mutagen import File  # For metadata handling


class AudioConverter(BaseConverter):
    def get_supported_formats(self):
        return [".mp3", ".wav", ".ogg", ".m4a", ".flac"]

    def convert(self, input_path, output_path, options):
        try:
            audio = AudioSegment.from_file(input_path)

            if "trim" in options and options["trim"]:
                start_ms = options["trim"].get("start", 0) * 1000
                end_ms = options["trim"].get("end", len(audio) / 1000) * 1000
                audio = audio[start_ms:end_ms]

            if "volume" in options:
                audio = audio + options["volume"]
            
            output_format = options.get("format", "mp3").lower()
            bitrate = options.get("bitrate")

            audio.export(output_path, format=output_format, bitrate=bitrate)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to convert {input_path}:\n{e}")
            return False


class AudioConverterUI(BaseConverterUI):
    """UI for audio converter. Builds UI components inside a parent frame."""
    
    def __init__(self, parent_frame: ctk.CTkFrame):
        """Initialize the audio converter UI."""
        self.converter = AudioConverter()
        super().__init__(parent_frame)

    def has_tabs(self) -> bool:
        """Audio converter uses tabs."""
        return True

    def setup_tabs(self):
        """Setup the audio converter tabs."""
        self.converter_tab = self.tab_view.add("Audio Converter")
        self.downloader_tab = self.tab_view.add("YouTube Downloader")
        self.tts_tab = self.tab_view.add("Text to Speech")
        self.stt_tab = self.tab_view.add("Speech to Text")
        self.recorder_tab = self.tab_view.add("Voice Recorder")
        self.tools_tab = self.tab_view.add("Audio Tools")
        self.metadata_tab = self.tab_view.add("Metadata Editor")

        # Configure grid for responsive layout
        for tab in [self.converter_tab, self.downloader_tab, self.tts_tab, self.stt_tab, self.recorder_tab, self.tools_tab, self.metadata_tab]:
            tab.grid_rowconfigure(0, weight=1)
            tab.grid_columnconfigure(0, weight=1)

    def build_ui(self):
        """Create the audio converter UI within the parent frame."""
        # Build converter tab UI
        self.setup_converter_tab()
        self.setup_downloader_tab()
        self.setup_tts_tab()
        self.setup_stt_tab()
        self.setup_recorder_tab()
        self.setup_tools_tab()
        self.setup_metadata_tab()

    def setup_downloader_tab(self):
        """Setup the YouTube downloader tab."""
        content_frame = ctk.CTkFrame(self.downloader_tab, fg_color="transparent")
        content_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # URL entry
        url_frame = ctk.CTkFrame(content_frame)
        url_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        url_frame.grid_columnconfigure(1, weight=1)

        url_label = ctk.CTkLabel(url_frame, text="YouTube URL:")
        url_label.grid(row=0, column=0, padx=(0, 5))

        self.url_var = ctk.StringVar()
        url_entry = ctk.CTkEntry(url_frame, textvariable=self.url_var, placeholder_text="Enter YouTube URL")
        url_entry.grid(row=0, column=1, sticky="ew")

        # Download options
        download_options_frame = ctk.CTkFrame(content_frame)
        download_options_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        self.download_type_var = ctk.StringVar(value="audio")
        audio_radio = ctk.CTkRadioButton(download_options_frame, text="Audio only (MP3)", 
                                       variable=self.download_type_var, value="audio")
        audio_radio.grid(row=0, column=0, padx=(0, 10))
        video_radio = ctk.CTkRadioButton(download_options_frame, text="Video (MP4)", 
                                       variable=self.download_type_var, value="video")
        video_radio.grid(row=0, column=1)

        # Action button
        self.download_button = ctk.CTkButton(content_frame, text="Download", command=self.download_youtube_video)
        self.download_button.grid(row=2, column=0, pady=(0, 5))

        # Progress bar
        self.download_progress = ctk.CTkProgressBar(content_frame)
        self.download_progress.grid(row=3, column=0, sticky="ew")
        self.download_progress.set(0)

    def setup_tts_tab(self):
        """Setup the Text-to-Speech tab."""
        content_frame = ctk.CTkFrame(self.tts_tab, fg_color="transparent")
        content_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Text input
        text_label = ctk.CTkLabel(content_frame, text="Enter Text:")
        text_label.grid(row=0, column=0, sticky="w")
        self.tts_text = ctk.CTkTextbox(content_frame, height=100)
        self.tts_text.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        # Voice selection
        voice_frame = ctk.CTkFrame(content_frame)
        voice_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        voice_frame.grid_columnconfigure(1, weight=1)
        
        voice_label = ctk.CTkLabel(voice_frame, text="Voice:")
        voice_label.grid(row=0, column=0, padx=(0, 5))
        self.tts_voice_var = ctk.StringVar()
        voice_menu = ctk.CTkOptionMenu(voice_frame, variable=self.tts_voice_var, 
                                     values=["Default Voice"])
        voice_menu.grid(row=0, column=1, padx=(0, 10))

        # Action buttons
        action_frame = ctk.CTkFrame(content_frame)
        action_frame.grid(row=3, column=0, sticky="ew")
        
        self.tts_button = ctk.CTkButton(action_frame, text="Convert to Speech", command=self.convert_to_speech)
        self.tts_button.grid(row=0, column=0, padx=(0, 5))
        
        self.play_button = ctk.CTkButton(action_frame, text="Play", command=self.play_speech, state="disabled")
        self.play_button.grid(row=0, column=1, padx=(0, 5))
        
        self.save_button = ctk.CTkButton(action_frame, text="Save As...", command=self.save_speech, state="disabled")
        self.save_button.grid(row=0, column=2)

    def setup_stt_tab(self):
        """Setup the Speech-to-Text tab."""
        content_frame = ctk.CTkFrame(self.stt_tab, fg_color="transparent")
        content_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        content_frame.grid_rowconfigure(1, weight=1)

        # File selection
        file_frame = ctk.CTkFrame(content_frame)
        file_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        file_frame.grid_columnconfigure(0, weight=1)
        
        self.stt_filepath_var = ctk.StringVar()
        file_entry = ctk.CTkEntry(file_frame, textvariable=self.stt_filepath_var, 
                                placeholder_text="Select an audio file", state="disabled")
        file_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        select_button = ctk.CTkButton(file_frame, text="Browse", command=self.select_stt_file)
        select_button.grid(row=0, column=1)

        # Transcription output
        self.stt_output = ctk.CTkTextbox(content_frame, height=150)
        self.stt_output.grid(row=1, column=0, sticky="nsew", pady=(0, 10))

        # Action buttons
        action_frame = ctk.CTkFrame(content_frame)
        action_frame.grid(row=2, column=0, sticky="ew")
        
        self.stt_start_button = ctk.CTkButton(action_frame, text="Start Transcription", 
                                             command=self.start_transcription, state="disabled")
        self.stt_start_button.grid(row=0, column=0, padx=(0, 5))
        
        self.stt_save_button = ctk.CTkButton(action_frame, text="Save As...", 
                                            command=self.save_transcription, state="disabled")
        self.stt_save_button.grid(row=0, column=1)

    def setup_recorder_tab(self):
        """Setup the Voice Recorder tab."""
        content_frame = ctk.CTkFrame(self.recorder_tab, fg_color="transparent")
        content_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Recording controls
        self.record_button = ctk.CTkButton(content_frame, text="Start Recording", command=self.start_recording)
        self.record_button.grid(row=0, column=0, pady=5)
        
        self.stop_button = ctk.CTkButton(content_frame, text="Stop Recording", 
                                        command=self.stop_recording, state="disabled")
        self.stop_button.grid(row=1, column=0, pady=5)
        
        # Recording status
        self.recording_status_var = ctk.StringVar(value="Status: Idle")
        status_label = ctk.CTkLabel(content_frame, textvariable=self.recording_status_var)
        status_label.grid(row=2, column=0, pady=5)

        # Post-recording actions
        self.post_rec_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        self.post_rec_frame.grid(row=3, column=0, pady=5)
        
        self.save_rec_button = ctk.CTkButton(self.post_rec_frame, text="Save Recording", 
                                            command=self.save_recording, state="disabled")
        self.save_rec_button.grid(row=0, column=0, padx=5)
        
        self.transcribe_rec_button = ctk.CTkButton(self.post_rec_frame, text="Transcribe", 
                                                  command=self.transcribe_recording, state="disabled")
        self.transcribe_rec_button.grid(row=0, column=1, padx=5)

    def setup_tools_tab(self):
        """Setup the Audio Tools tab."""
        content_frame = ctk.CTkFrame(self.tools_tab, fg_color="transparent")
        content_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Audio effects section
        effects_frame = ctk.CTkFrame(content_frame)
        effects_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        effects_label = ctk.CTkLabel(effects_frame, text="Audio Effects")
        effects_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)

        # Effect options
        self.reverb_var = ctk.BooleanVar()
        reverb_cb = ctk.CTkCheckBox(effects_frame, text="Reverb", variable=self.reverb_var)
        reverb_cb.grid(row=1, column=0, sticky="w", padx=5, pady=2)
        
        self.bass_boost_var = ctk.BooleanVar()
        bass_cb = ctk.CTkCheckBox(effects_frame, text="Bass Boost", variable=self.bass_boost_var)
        bass_cb.grid(row=2, column=0, sticky="w", padx=5, pady=2)
        
        # Speed control
        speed_frame = ctk.CTkFrame(effects_frame)
        speed_frame.grid(row=3, column=0, sticky="ew", padx=5, pady=2)
        speed_frame.grid_columnconfigure(1, weight=1)
        
        speed_label = ctk.CTkLabel(speed_frame, text="Speed:")
        speed_label.grid(row=0, column=0)
        
        self.speed_var = ctk.DoubleVar(value=1.0)
        speed_slider = ctk.CTkSlider(speed_frame, from_=0.5, to=2.0, variable=self.speed_var)
        speed_slider.grid(row=0, column=1, sticky="ew", padx=5)

    def setup_metadata_tab(self):
        """Setup the Metadata Editor tab."""
        content_frame = ctk.CTkFrame(self.metadata_tab, fg_color="transparent")
        content_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # File selection
        file_frame = ctk.CTkFrame(content_frame)
        file_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        file_frame.grid_columnconfigure(0, weight=1)
        
        self.metadata_filepath_var = ctk.StringVar()
        file_entry = ctk.CTkEntry(file_frame, textvariable=self.metadata_filepath_var, 
                                 placeholder_text="Select an audio file", state="disabled")
        file_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        select_button = ctk.CTkButton(file_frame, text="Browse", command=self.select_metadata_file)
        select_button.grid(row=0, column=1)

        # Metadata fields
        fields_frame = ctk.CTkFrame(content_frame)
        fields_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        # Title
        title_label = ctk.CTkLabel(fields_frame, text="Title:")
        title_label.grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.title_var = ctk.StringVar()
        title_entry = ctk.CTkEntry(fields_frame, textvariable=self.title_var)
        title_entry.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 5))
        
        # Artist
        artist_label = ctk.CTkLabel(fields_frame, text="Artist:")
        artist_label.grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.artist_var = ctk.StringVar()
        artist_entry = ctk.CTkEntry(fields_frame, textvariable=self.artist_var)
        artist_entry.grid(row=3, column=0, sticky="ew", padx=5, pady=(0, 5))
        
        # Album
        album_label = ctk.CTkLabel(fields_frame, text="Album:")
        album_label.grid(row=4, column=0, sticky="w", padx=5, pady=2)
        self.album_var = ctk.StringVar()
        album_entry = ctk.CTkEntry(fields_frame, textvariable=self.album_var)
        album_entry.grid(row=5, column=0, sticky="ew", padx=5, pady=(0, 5))

        # Save button
        save_button = ctk.CTkButton(content_frame, text="Save Metadata", command=self.save_metadata)
        save_button.grid(row=2, column=0, pady=5)

    def setup_converter_tab(self):
        """Setup the main converter tab."""
        content_frame = ctk.CTkFrame(self.converter_tab, fg_color="transparent")
        content_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        self.create_file_selection_area(content_frame)
        self.create_conversion_options(content_frame)
        self.create_output_options(content_frame)
        self.create_action_area(content_frame)

    def create_file_selection_area(self, parent):
        """Create the file selection area."""
        file_frame = ctk.CTkFrame(parent)
        file_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        file_frame.grid_columnconfigure(1, weight=1)

        select_button = ctk.CTkButton(file_frame, text="Select Audio Files", command=self.browse_files)
        select_button.grid(row=0, column=0, padx=2, pady=2)

        self.file_listbox = Listbox(file_frame, selectmode=MULTIPLE, bg="#2b2b2b", fg="white", 
                                  borderwidth=0, highlightthickness=0)
        self.file_listbox.grid(row=0, column=1, padx=2, pady=2, sticky="nsew")

        scrollbar = Scrollbar(file_frame, orient="vertical", command=self.file_listbox.yview)
        scrollbar.grid(row=0, column=2, sticky="ns")
        self.file_listbox.config(yscrollcommand=scrollbar.set)

        clear_button = ctk.CTkButton(file_frame, text="Clear", command=self.clear_files)
        clear_button.grid(row=0, column=3, padx=2, pady=2)

    def create_conversion_options(self, parent):
        """Create the conversion options area."""
        options_frame = ctk.CTkFrame(parent)
        options_frame.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        # Format selection
        format_label = ctk.CTkLabel(options_frame, text="Convert to:")
        format_label.grid(row=0, column=0, padx=(0, 2))
        self.format_var = ctk.StringVar(value="mp3")
        format_menu = ctk.CTkOptionMenu(options_frame, variable=self.format_var,
                                      values=["mp3", "wav", "ogg", "m4a", "flac"])
        format_menu.grid(row=0, column=1, padx=2)

        # Bitrate selection
        bitrate_label = ctk.CTkLabel(options_frame, text="Bitrate:")
        bitrate_label.grid(row=0, column=2, padx=(10, 2))
        self.bitrate_var = ctk.StringVar(value="192k")
        bitrate_menu = ctk.CTkOptionMenu(options_frame, variable=self.bitrate_var,
                                       values=["128k", "192k", "256k", "320k"])
        bitrate_menu.grid(row=0, column=3, padx=2)

        # Volume adjustment
        volume_label = ctk.CTkLabel(options_frame, text="Volume:")
        volume_label.grid(row=0, column=4, padx=(10, 2))
        self.volume_var = ctk.DoubleVar(value=0)
        volume_slider = ctk.CTkSlider(options_frame, from_=-10, to=10,
                                    variable=self.volume_var)
        volume_slider.grid(row=0, column=5, padx=2)
        volume_value = ctk.CTkLabel(options_frame, textvariable=self.volume_var)
        volume_value.grid(row=0, column=6, padx=2)

    def create_output_options(self, parent):
        """Create the output options area."""
        output_frame = ctk.CTkFrame(parent)
        output_frame.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        output_frame.grid_columnconfigure(1, weight=1)

        output_button = ctk.CTkButton(output_frame, text="Output Folder",
                                    command=self.browse_output)
        output_button.grid(row=0, column=0, padx=(0, 5))

        self.output_label = ctk.CTkLabel(output_frame, text="No output folder selected")
        self.output_label.grid(row=0, column=1, sticky="ew")

    def create_action_area(self, parent):
        """Create the action area with conversion button and progress bar."""
        action_frame = ctk.CTkFrame(parent)
        action_frame.grid(row=3, column=0, padx=5, pady=5, sticky="ew")
        action_frame.grid_columnconfigure(1, weight=1)

        self.convert_button = ctk.CTkButton(action_frame, text="Start Conversion",
                                          command=self.start_conversion)
        self.convert_button.grid(row=0, column=0, padx=(0, 5))

        self.progress_bar = ctk.CTkProgressBar(action_frame)
        self.progress_bar.grid(row=0, column=1, sticky="ew")
        self.progress_bar.set(0)

    def download_youtube_video(self):
        """Download video from YouTube URL."""
        url = self.url_var.get()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL.")
            return

        download_type = self.download_type_var.get()
        
        output_path = filedialog.askdirectory(title="Select Download Folder")
        if not output_path:
            return

        self.download_button.configure(state="disabled")
        self.download_progress.set(0)
        threading.Thread(target=self._download_thread, args=(url, download_type, output_path), daemon=True).start()

    def _download_thread(self, url, download_type, output_path):
        """Background thread for downloading YouTube content."""
        try:
            import yt_dlp

            ydl_opts = {
                'format': 'bestaudio/best' if download_type == 'audio' else 'best',
                'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
                'progress_hooks': [self.download_progress_hook],
            }

            if download_type == 'audio':
                ydl_opts.update({
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                })

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                
            messagebox.showinfo("Success", "Download completed successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to download: {str(e)}")
        finally:
            self.download_button.configure(state="normal")

    def download_progress_hook(self, d):
        """Update progress bar during download."""
        if d['status'] == 'downloading':
            try:
                progress = float(d['downloaded_bytes']) / float(d['total_bytes'])
                self.download_progress.set(progress)
            except:
                pass  # Some videos might not have size info
        elif d['status'] == 'finished':
            self.download_progress.set(1)

    def convert_to_speech(self):
        """Convert text to speech."""
        text = self.tts_text.get("1.0", "end-1c")
        if not text:
            messagebox.showerror("Error", "Please enter some text.")
            return

        voice = self.tts_voice_var.get()

        self.tts_button.configure(state="disabled")
        threading.Thread(target=self._convert_to_speech_thread, args=(text, voice), daemon=True).start()

    def _convert_to_speech_thread(self, text, voice):
        """Background thread for text-to-speech conversion."""
        try:
            import pyttsx3

            engine = pyttsx3.init()
            
            # Set voice if specified
            if voice != "Default Voice":
                engine.setProperty('voice', voice)

            # Save as temporary WAV file
            self.tts_audio_path = "temp_tts.wav"
            engine.save_to_file(text, self.tts_audio_path)
            engine.runAndWait()

            self.play_button.configure(state="normal")
            self.save_button.configure(state="normal")
            messagebox.showinfo("Success", "Text converted to speech.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to convert text to speech: {str(e)}")
        finally:
            self.tts_button.configure(state="normal")

    def play_speech(self):
        """Play the generated speech audio."""
        if not hasattr(self, 'tts_audio_path') or not os.path.exists(self.tts_audio_path):
            messagebox.showerror("Error", "No audio available to play.")
            return

        try:
            import pygame
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            
            pygame.mixer.music.load(self.tts_audio_path)
            pygame.mixer.music.play()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to play audio: {str(e)}")

    def save_speech(self):
        """Save the generated speech audio."""
        if not hasattr(self, 'tts_audio_path') or not os.path.exists(self.tts_audio_path):
            messagebox.showerror("Error", "No audio available to save.")
            return

        save_path = filedialog.asksaveasfilename(
            title="Save Audio File",
            defaultextension=".wav",
            filetypes=[("WAV files", "*.wav"), ("MP3 files", "*.mp3"), ("All files", "*.*")]
        )
        if save_path:
            try:
                import shutil
                shutil.copy2(self.tts_audio_path, save_path)
                messagebox.showinfo("Success", "Audio saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save audio: {str(e)}")

    def select_stt_file(self):
        """Select audio file for speech-to-text conversion."""
        filepath = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=[("Audio Files", "*.wav *.mp3 *.m4a"), ("All files", "*.*")]
        )
        if filepath:
            self.stt_filepath_var.set(filepath)
            self.stt_start_button.configure(state="normal")

    def start_transcription(self):
        """Start the transcription process."""
        filepath = self.stt_filepath_var.get()
        if not filepath or not os.path.exists(filepath):
            messagebox.showerror("Error", "Please select a valid audio file.")
            return

        self.stt_start_button.configure(state="disabled")
        self.stt_output.delete("1.0", "end")
        threading.Thread(target=self._transcription_thread, args=(filepath,), daemon=True).start()

    def _transcription_thread(self, filepath):
        """Background thread for speech-to-text transcription."""
        try:
            import speech_recognition as sr
            
            r = sr.Recognizer()
            with sr.AudioFile(filepath) as source:
                audio = r.record(source)
            
            # Using Google's speech recognition
            text = r.recognize_google(audio)
            
            # Update UI
            self.stt_output.insert("1.0", text)
            self.stt_save_button.configure(state="normal")
            messagebox.showinfo("Success", "Transcription complete!")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to transcribe audio: {str(e)}")
        finally:
            self.stt_start_button.configure(state="normal")

    def save_transcription(self):
        """Save the transcription text to a file."""
        text = self.stt_output.get("1.0", "end-1c")
        if not text:
            messagebox.showerror("Error", "No transcription to save.")
            return

        save_path = filedialog.asksaveasfilename(
            title="Save Transcription",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if save_path:
            try:
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                messagebox.showinfo("Success", "Transcription saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save transcription: {str(e)}")

    def start_recording(self):
        """Start audio recording."""
        try:
            import pyaudio
            import wave

            self.record_button.configure(state="disabled")
            self.stop_button.configure(state="normal")
            self.save_rec_button.configure(state="disabled")
            self.transcribe_rec_button.configure(state="disabled")
            self.post_rec_frame.pack_forget()

            self.is_recording = True
            self.recording_status_var.set("Status: Recording...")
            self.audio_frames = []
            
            # Initialize PyAudio
            self.pyaudio_instance = pyaudio.PyAudio()
            self.audio_stream = self.pyaudio_instance.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=44100,
                input=True,
                frames_per_buffer=1024,
                stream_callback=self.audio_callback
            )
            self.audio_stream.start_stream()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to start recording: {str(e)}")
            self.record_button.configure(state="normal")

    def stop_recording(self):
        """Stop audio recording."""
        if not hasattr(self, 'is_recording') or not self.is_recording:
            return
            
        self.is_recording = False
        self.recording_status_var.set("Status: Stopped")
        
        # Stop and clean up audio stream
        if hasattr(self, 'audio_stream'):
            self.audio_stream.stop_stream()
            self.audio_stream.close()
        if hasattr(self, 'pyaudio_instance'):
            self.pyaudio_instance.terminate()

        # Update UI
        self.record_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.save_rec_button.configure(state="normal")
        self.transcribe_rec_button.configure(state="normal")
        self.post_rec_frame.pack(pady=10)

        # Save to temporary file
        self.recorded_audio_path = "temp_recording.wav"
        with wave.open(self.recorded_audio_path, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(self.pyaudio_instance.get_sample_size(pyaudio.paInt16))
            wf.setframerate(44100)
            wf.writeframes(b''.join(self.audio_frames))

    def audio_callback(self, in_data, frame_count, time_info, status):
        """Callback for audio recording."""
        if self.is_recording:
            self.audio_frames.append(in_data)
        return (in_data, pyaudio.paContinue)

    def save_recording(self):
        """Save the recorded audio to a file."""
        if not hasattr(self, 'recorded_audio_path') or not os.path.exists(self.recorded_audio_path):
            messagebox.showerror("Error", "No recording to save.")
            return

        save_path = filedialog.asksaveasfilename(
            title="Save Recording",
            defaultextension=".wav",
            filetypes=[("WAV files", "*.wav"), ("MP3 files", "*.mp3"), ("All files", "*.*")]
        )
        if save_path:
            try:
                import shutil
                shutil.copy2(self.recorded_audio_path, save_path)
                messagebox.showinfo("Success", "Recording saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save recording: {str(e)}")

    def transcribe_recording(self):
        """Transcribe the recorded audio."""
        if not hasattr(self, 'recorded_audio_path') or not os.path.exists(self.recorded_audio_path):
            messagebox.showerror("Error", "No recording to transcribe.")
            return

        # Set the file path in STT tab and switch to it
        self.stt_filepath_var.set(self.recorded_audio_path)
        self.tab_view.set("Speech to Text")
        self.start_transcription()

    def select_metadata_file(self):
        """Select audio file for metadata editing."""
        filepath = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=[("Audio Files", "*.mp3 *.wav *.m4a *.flac"), ("All files", "*.*")]
        )
        if filepath:
            self.metadata_filepath_var.set(filepath)
            self.load_metadata(filepath)

    def load_metadata(self, filepath):
        """Load metadata from the selected audio file."""
        try:
            from mutagen import File
            audio = File(filepath)
            
            if audio is None:
                messagebox.showerror("Error", "Could not read metadata from this file.")
                return

            # Clear existing values
            self.title_var.set("")
            self.artist_var.set("")
            self.album_var.set("")

            # Try to load metadata based on file format
            if hasattr(audio, 'tags'):  # MP3, FLAC
                tags = audio.tags
                if tags:
                    self.title_var.set(tags.get('title', [''])[0] if isinstance(tags.get('title'), list) else tags.get('title', ''))
                    self.artist_var.set(tags.get('artist', [''])[0] if isinstance(tags.get('artist'), list) else tags.get('artist', ''))
                    self.album_var.set(tags.get('album', [''])[0] if isinstance(tags.get('album'), list) else tags.get('album', ''))
            else:  # Other formats
                self.title_var.set(getattr(audio, 'title', ''))
                self.artist_var.set(getattr(audio, 'artist', ''))
                self.album_var.set(getattr(audio, 'album', ''))

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load metadata: {str(e)}")

    def save_metadata(self):
        """Save metadata to the audio file."""
        filepath = self.metadata_filepath_var.get()
        if not filepath or not os.path.exists(filepath):
            messagebox.showerror("Error", "Please select an audio file first.")
            return

        try:
            from mutagen import File
            audio = File(filepath)
            
            if audio is None:
                messagebox.showerror("Error", "Could not read file for metadata editing.")
                return

            # Update metadata based on file format
            if hasattr(audio, 'tags'):  # MP3, FLAC
                if audio.tags is None:
                    audio.add_tags()
                
                audio.tags['title'] = self.title_var.get()
                audio.tags['artist'] = self.artist_var.get()
                audio.tags['album'] = self.album_var.get()
            else:  # Other formats
                audio['title'] = self.title_var.get()
                audio['artist'] = self.artist_var.get()
                audio['album'] = self.album_var.get()

            audio.save()
            messagebox.showinfo("Success", "Metadata saved successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save metadata: {str(e)}")

    def browse_files(self):
        """Browse for input files."""
        files = filedialog.askopenfilenames(
            title="Select Audio Files",
            filetypes=[
                ("Audio Files", "*.mp3 *.wav *.ogg *.m4a *.flac"),
                ("All Files", "*.*")
            ]
        )
        if files:
            self.input_files.extend(list(files))
            self.update_file_list()

    def clear_files(self):
        """Clear selected files."""
        self.input_files = []
        self.update_file_list()

    def update_file_list(self):
        """Update the file list display."""
        self.file_listbox.delete(0, "end")
        for file in self.input_files:
            self.file_listbox.insert("end", os.path.basename(file))

    def browse_output(self):
        """Browse for output directory."""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir = directory
            self.output_label.configure(text=directory)

    def start_conversion(self):
        """Start the conversion process."""
        if not self.input_files:
            messagebox.showwarning("Warning", "Please select input files first!")
            return

        if not self.output_dir:
            messagebox.showwarning("Warning", "Please select output directory first!")
            return

        self.convert_button.configure(state="disabled")
        self.progress_bar.set(0)
        total_files = len(self.input_files)

        for i, input_file in enumerate(self.input_files):
            output_filename = os.path.splitext(os.path.basename(input_file))[0]
            output_filename = f"{output_filename}.{self.format_var.get()}"
            output_path = os.path.join(self.output_dir, output_filename)

            options = {
                "format": self.format_var.get(),
                "bitrate": self.bitrate_var.get(),
                "volume": self.volume_var.get()
            }

            success = self.converter.convert(input_file, output_path, options)
            if success:
                progress = (i + 1) / total_files
                self.progress_bar.set(progress)

        self.convert_button.configure(state="normal")
        messagebox.showinfo("Success", "Conversion complete!")