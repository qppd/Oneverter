import customtkinter as ctk
from tkinter import filedialog, Listbox, Scrollbar, MULTIPLE, END, messagebox
from .base_window import BaseWindow
from converters.audio_converter import AudioConverter
import os
import yt_dlp
import threading
import pyttsx3
import pygame
from vosk import Model, KaldiRecognizer
import json
import wave
import pyaudio
from pydub import AudioSegment
from pydub.silence import split_on_silence
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from .animated_spinner import AnimatedSpinner

class AudioConverterWindow(BaseWindow):
    def __init__(self, parent):
        super().__init__(parent, title="Oneverter - Audio Converter", geometry="1024x768")
        self.converter = AudioConverter()

        # Initialize pyttsx3 engine
        self.tts_engine = pyttsx3.init()
        self.voices = self.tts_engine.getProperty('voices')
        self.voice_map = {f"{v.name} ({v.gender})": v.id for v in self.voices}

        self.create_widgets()
        
        # Create a single loading spinner for the window
        self.loading_spinner = AnimatedSpinner(self, "assets/loading_spinner.gif")

    def show_loading(self):
        """Show the loading spinner."""
        self.loading_spinner.show()

    def hide_loading(self):
        """Hide the loading spinner."""
        self.loading_spinner.hide()

    def create_widgets(self):
        # Header
        header_frame = ctk.CTkFrame(self)
        header_frame.pack(padx=20, pady=20, fill="x")

        back_button = ctk.CTkButton(header_frame, text="← Back to Converters", command=self.on_close, width=150)
        back_button.pack(side="left")

        title_label = ctk.CTkLabel(header_frame, text="🎵 Audio Converter", font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(side="left", padx=20)

        # Tab view for different tools
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.pack(padx=20, pady=(0, 20), fill="both", expand=True)

        self.converter_tab = self.tab_view.add("Audio Converter")
        self.downloader_tab = self.tab_view.add("YouTube Downloader")
        self.tts_tab = self.tab_view.add("Text to Speech")
        self.stt_tab = self.tab_view.add("Speech to Text")
        self.recorder_tab = self.tab_view.add("Voice Recorder")
        self.tools_tab = self.tab_view.add("Audio Tools")
        self.metadata_tab = self.tab_view.add("Metadata Editor")

        self.setup_converter_tab()
        self.setup_downloader_tab()
        self.setup_tts_tab()
        self.setup_stt_tab()
        self.setup_recorder_tab()
        self.setup_tools_tab()
        self.setup_metadata_tab()

    def setup_converter_tab(self):
        # Main content frame
        content_frame = ctk.CTkFrame(self.converter_tab, fg_color="transparent")
        content_frame.pack(padx=20, pady=(0, 20), fill="both", expand=True)

        # File selection
        selection_frame = ctk.CTkFrame(content_frame)
        selection_frame.pack(padx=10, pady=10, fill="x")

        select_button = ctk.CTkButton(selection_frame, text="Select Audio Files", command=self.select_files)
        select_button.pack(side="left", padx=(0, 10))

        self.file_listbox = Listbox(selection_frame, selectmode=MULTIPLE, bg="#2b2b2b", fg="white", borderwidth=0, highlightthickness=0)
        self.file_listbox.pack(side="left", fill="both", expand=True)

        scrollbar = Scrollbar(selection_frame, orient="vertical", command=self.file_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.file_listbox.config(yscrollcommand=scrollbar.set)

        # Conversion options
        options_frame = ctk.CTkFrame(content_frame)
        options_frame.pack(padx=10, pady=10, fill="x", anchor="w")

        format_label = ctk.CTkLabel(options_frame, text="Convert to:")
        format_label.pack(side="left", padx=(0, 10))
        self.format_var = ctk.StringVar(value="mp3")
        format_menu = ctk.CTkOptionMenu(options_frame, variable=self.format_var, values=["mp3", "wav", "ogg", "m4a", "flac"])
        format_menu.pack(side="left", padx=(0, 20))

        bitrate_label = ctk.CTkLabel(options_frame, text="Bitrate:")
        bitrate_label.pack(side="left", padx=(0, 10))
        self.bitrate_var = ctk.StringVar(value="192k")
        bitrate_menu = ctk.CTkOptionMenu(options_frame, variable=self.bitrate_var, values=["128k", "192k", "256k", "320k"])
        bitrate_menu.pack(side="left", padx=(0, 20))

        # Audio editing options
        edit_frame = ctk.CTkFrame(content_frame)
        edit_frame.pack(padx=10, pady=10, fill="x", anchor="w")

        trim_label = ctk.CTkLabel(edit_frame, text="Trim (s):")
        trim_label.pack(side="left", padx=(0, 10))
        self.start_trim_var = ctk.StringVar(value="0")
        self.end_trim_var = ctk.StringVar()
        start_trim_entry = ctk.CTkEntry(edit_frame, textvariable=self.start_trim_var, width=60)
        start_trim_entry.pack(side="left")
        end_trim_entry = ctk.CTkEntry(edit_frame, textvariable=self.end_trim_var, width=60, placeholder_text="End")
        end_trim_entry.pack(side="left", padx=(5, 20))

        volume_label = ctk.CTkLabel(edit_frame, text="Volume (dB):")
        volume_label.pack(side="left", padx=(0, 10))
        self.volume_var = ctk.DoubleVar(value=0)
        volume_slider = ctk.CTkSlider(edit_frame, from_=-10, to=10, variable=self.volume_var)
        volume_slider.pack(side="left")
        volume_value_label = ctk.CTkLabel(edit_frame, textvariable=self.volume_var, width=4)
        volume_value_label.pack(side="left", padx=(5, 0))
        
        # Output
        output_frame = ctk.CTkFrame(content_frame)
        output_frame.pack(padx=10, pady=10, fill="x")

        output_button = ctk.CTkButton(output_frame, text="Output Folder", command=self.select_output_folder)
        output_button.pack(side="left", padx=(0, 10))

        self.output_folder_var = ctk.StringVar(value="Same folder")
        output_label = ctk.CTkLabel(output_frame, textvariable=self.output_folder_var, fg_color="#2b2b2b", text_color="white", corner_radius=5)
        output_label.pack(side="left", fill="x", expand=True)

        self.same_folder_var = ctk.BooleanVar(value=True)
        same_folder_check = ctk.CTkCheckBox(output_frame, text="Save in same folder", variable=self.same_folder_var, command=self.toggle_output_folder)
        same_folder_check.pack(side="left", padx=(10, 0))

        # Actions
        action_frame = ctk.CTkFrame(content_frame)
        action_frame.pack(padx=10, pady=10, fill="x")

        self.start_button = ctk.CTkButton(action_frame, text="Start Conversion", command=self.start_conversion)
        self.start_button.pack(side="left", padx=(0, 10))

        self.progress_bar = ctk.CTkProgressBar(action_frame)
        self.progress_bar.pack(side="left", fill="x", expand=True)
        self.progress_bar.set(0)

    def setup_downloader_tab(self):
        downloader_frame = ctk.CTkFrame(self.downloader_tab, fg_color="transparent")
        downloader_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # URL entry
        url_frame = ctk.CTkFrame(downloader_frame)
        url_frame.pack(fill="x", pady=(0, 20))

        url_label = ctk.CTkLabel(url_frame, text="YouTube URL:")
        url_label.pack(side="left", padx=(0, 10))

        self.url_var = ctk.StringVar()
        url_entry = ctk.CTkEntry(url_frame, textvariable=self.url_var, placeholder_text="Enter YouTube URL")
        url_entry.pack(side="left", fill="x", expand=True)

        # Download options
        download_options_frame = ctk.CTkFrame(downloader_frame)
        download_options_frame.pack(fill="x", pady=(0, 20))

        self.download_type_var = ctk.StringVar(value="audio")
        audio_radio = ctk.CTkRadioButton(download_options_frame, text="Audio only (MP3)", variable=self.download_type_var, value="audio")
        audio_radio.pack(side="left", padx=(0, 20))
        video_radio = ctk.CTkRadioButton(download_options_frame, text="Video (MP4)", variable=self.download_type_var, value="video")
        video_radio.pack(side="left")

        # Action button
        self.download_button = ctk.CTkButton(downloader_frame, text="Download", command=self.download_youtube_video)
        self.download_button.pack(pady=(0, 10))

        # Progress bar
        self.download_progress = ctk.CTkProgressBar(downloader_frame)
        self.download_progress.pack(fill="x")
        self.download_progress.set(0)

    def setup_tts_tab(self):
        tts_frame = ctk.CTkFrame(self.tts_tab, fg_color="transparent")
        tts_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Text input
        text_label = ctk.CTkLabel(tts_frame, text="Enter Text:")
        text_label.pack(anchor="w")
        self.tts_text = ctk.CTkTextbox(tts_frame, height=150)
        self.tts_text.pack(fill="x", pady=(0, 20))

        # Options
        options_frame = ctk.CTkFrame(tts_frame)
        options_frame.pack(fill="x", pady=(0, 20))

        voice_label = ctk.CTkLabel(options_frame, text="Voice:")
        voice_label.pack(side="left", padx=(0, 10))
        self.tts_voice_var = ctk.StringVar(value=list(self.voice_map.keys())[0])
        voice_menu = ctk.CTkOptionMenu(options_frame, variable=self.tts_voice_var, values=list(self.voice_map.keys()))
        voice_menu.pack(side="left", padx=(0, 20))

        # Actions
        action_frame = ctk.CTkFrame(tts_frame)
        action_frame.pack(fill="x")
        
        self.tts_button = ctk.CTkButton(action_frame, text="Convert to Speech", command=self.convert_to_speech)
        self.tts_button.pack(side="left", padx=(0, 10))
        
        self.play_button = ctk.CTkButton(action_frame, text="Play", command=self.play_speech, state="disabled")
        self.play_button.pack(side="left", padx=(0, 10))
        
        self.save_button = ctk.CTkButton(action_frame, text="Save As...", command=self.save_speech, state="disabled")
        self.save_button.pack(side="left")

        pygame.mixer.init()
        self.tts_audio_path = None

    def setup_stt_tab(self):
        stt_frame = ctk.CTkFrame(self.stt_tab, fg_color="transparent")
        stt_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # File selection
        stt_file_frame = ctk.CTkFrame(stt_frame)
        stt_file_frame.pack(fill="x", pady=(0, 20))
        self.stt_filepath_var = ctk.StringVar()
        stt_file_entry = ctk.CTkEntry(stt_file_frame, textvariable=self.stt_filepath_var, placeholder_text="Select an audio file", state="disabled")
        stt_file_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        stt_select_button = ctk.CTkButton(stt_file_frame, text="Browse", command=self.select_stt_file)
        stt_select_button.pack(side="left")

        # Transcription output
        self.stt_output = ctk.CTkTextbox(stt_frame, height=200)
        self.stt_output.pack(fill="both", expand=True, pady=(0, 20))

        # Actions
        stt_action_frame = ctk.CTkFrame(stt_frame)
        stt_action_frame.pack(fill="x")
        self.stt_start_button = ctk.CTkButton(stt_action_frame, text="Start Transcription", command=self.start_transcription, state="disabled")
        self.stt_start_button.pack(side="left", padx=(0, 10))
        self.stt_save_button = ctk.CTkButton(stt_action_frame, text="Save As...", command=self.save_transcription, state="disabled")
        self.stt_save_button.pack(side="left")

    def setup_recorder_tab(self):
        recorder_frame = ctk.CTkFrame(self.recorder_tab, fg_color="transparent")
        recorder_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Recording controls
        self.record_button = ctk.CTkButton(recorder_frame, text="Start Recording", command=self.start_recording)
        self.record_button.pack(pady=10)
        self.stop_button = ctk.CTkButton(recorder_frame, text="Stop Recording", command=self.stop_recording, state="disabled")
        self.stop_button.pack(pady=10)
        
        # Recording status
        self.recording_status_var = ctk.StringVar(value="Status: Idle")
        recording_status_label = ctk.CTkLabel(recorder_frame, textvariable=self.recording_status_var)
        recording_status_label.pack(pady=10)

        # Post-recording actions
        self.post_rec_frame = ctk.CTkFrame(recorder_frame, fg_color="transparent")
        self.save_rec_button = ctk.CTkButton(self.post_rec_frame, text="Save Recording", command=self.save_recording, state="disabled")
        self.save_rec_button.pack(side="left", padx=10)
        self.transcribe_rec_button = ctk.CTkButton(self.post_rec_frame, text="Transcribe", command=self.transcribe_recording, state="disabled")
        self.transcribe_rec_button.pack(side="left", padx=10)

        self.is_recording = False
        self.audio_frames = []
        self.pyaudio_instance = None
        self.audio_stream = None
        self.recorded_audio_path = None

    def setup_tools_tab(self):
        tools_frame = ctk.CTkFrame(self.tools_tab, fg_color="transparent")
        tools_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Merge Audio Section
        merge_frame = ctk.CTkFrame(tools_frame)
        merge_frame.pack(fill="x", pady=(0, 20))
        
        merge_label = ctk.CTkLabel(merge_frame, text="Merge Audio Files", font=ctk.CTkFont(size=16, weight="bold"))
        merge_label.pack(anchor="w", padx=10, pady=10)
        
        # File list
        self.merge_listbox = Listbox(merge_frame, selectmode=MULTIPLE, bg="#2b2b2b", fg="white", borderwidth=0, highlightthickness=0)
        self.merge_listbox.pack(fill="x", padx=10, pady=10)

        # Buttons
        merge_button_frame = ctk.CTkFrame(merge_frame, fg_color="transparent")
        merge_button_frame.pack(fill="x", padx=10, pady=10)

        add_button = ctk.CTkButton(merge_button_frame, text="Add Files", command=self.add_merge_files)
        add_button.pack(side="left")
        remove_button = ctk.CTkButton(merge_button_frame, text="Remove Selected", command=self.remove_merge_files)
        remove_button.pack(side="left", padx=10)
        merge_action_button = ctk.CTkButton(merge_button_frame, text="Merge Files", command=self.merge_files)
        merge_action_button.pack(side="left", padx=10)

        # Split Audio Section
        split_frame = ctk.CTkFrame(tools_frame)
        split_frame.pack(fill="x", pady=20)

        split_label = ctk.CTkLabel(split_frame, text="Split Audio File", font=ctk.CTkFont(size=16, weight="bold"))
        split_label.pack(anchor="w", padx=10, pady=10)

        # File selection
        split_file_frame = ctk.CTkFrame(split_frame)
        split_file_frame.pack(fill="x", padx=10, pady=(0,10))
        self.split_filepath_var = ctk.StringVar()
        split_file_entry = ctk.CTkEntry(split_file_frame, textvariable=self.split_filepath_var, placeholder_text="Select an audio file to split", state="disabled")
        split_file_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        split_select_button = ctk.CTkButton(split_file_frame, text="Browse", command=self.select_split_file)
        split_select_button.pack(side="left")
        
        # Split options
        split_options_frame = ctk.CTkFrame(split_frame)
        split_options_frame.pack(fill="x", padx=10, pady=10)
        
        self.split_method_var = ctk.StringVar(value="silence")
        split_by_silence_radio = ctk.CTkRadioButton(split_options_frame, text="Split by Silence", variable=self.split_method_var, value="silence", command=self.toggle_split_options)
        split_by_silence_radio.pack(side="left", padx=(0, 20))
        split_by_time_radio = ctk.CTkRadioButton(split_options_frame, text="Split by Duration", variable=self.split_method_var, value="time", command=self.toggle_split_options)
        split_by_time_radio.pack(side="left")

        self.split_silence_frame = ctk.CTkFrame(split_options_frame, fg_color="transparent")
        self.split_silence_frame.pack(fill="x", pady=(10,0))
        ctk.CTkLabel(self.split_silence_frame, text="Min Silence (ms):").pack(side="left")
        self.min_silence_len_var = ctk.StringVar(value="1000")
        ctk.CTkEntry(self.split_silence_frame, textvariable=self.min_silence_len_var, width=60).pack(side="left", padx=(0, 20))
        ctk.CTkLabel(self.split_silence_frame, text="Silence Threshold (dB):").pack(side="left")
        self.silence_thresh_var = ctk.StringVar(value="-40")
        ctk.CTkEntry(self.split_silence_frame, textvariable=self.silence_thresh_var, width=60).pack(side="left")

        self.split_time_frame = ctk.CTkFrame(split_options_frame, fg_color="transparent")
        ctk.CTkLabel(self.split_time_frame, text="Duration (s):").pack(side="left")
        self.split_duration_var = ctk.StringVar(value="60")
        ctk.CTkEntry(self.split_time_frame, textvariable=self.split_duration_var, width=60).pack(side="left")

        self.toggle_split_options()

        # Action button
        split_action_button = ctk.CTkButton(split_frame, text="Split File", command=self.split_file)
        split_action_button.pack(pady=10)

        # Effects Section
        effects_frame = ctk.CTkFrame(tools_frame)
        effects_frame.pack(fill="x", pady=20)
        
        effects_label = ctk.CTkLabel(effects_frame, text="Audio Effects", font=ctk.CTkFont(size=16, weight="bold"))
        effects_label.pack(anchor="w", padx=10, pady=10)

        # File selection
        effects_file_frame = ctk.CTkFrame(effects_frame)
        effects_file_frame.pack(fill="x", padx=10, pady=(0,10))
        self.effects_filepath_var = ctk.StringVar()
        effects_file_entry = ctk.CTkEntry(effects_file_frame, textvariable=self.effects_filepath_var, placeholder_text="Select an audio file for effects", state="disabled")
        effects_file_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        effects_select_button = ctk.CTkButton(effects_file_frame, text="Browse", command=self.select_effects_file)
        effects_select_button.pack(side="left")

        # Effect options
        effects_options_frame = ctk.CTkFrame(effects_frame)
        effects_options_frame.pack(fill="x", padx=10, pady=10)

        self.reverb_var = ctk.BooleanVar()
        ctk.CTkCheckBox(effects_options_frame, text="Reverb", variable=self.reverb_var).pack(side="left", padx=(0, 20))
        self.bass_boost_var = ctk.BooleanVar()
        ctk.CTkCheckBox(effects_options_frame, text="Bass Boost", variable=self.bass_boost_var).pack(side="left", padx=(0, 20))
        self.reverse_var = ctk.BooleanVar()
        ctk.CTkCheckBox(effects_options_frame, text="Reverse", variable=self.reverse_var).pack(side="left", padx=(0, 20))
        
        ctk.CTkLabel(effects_options_frame, text="Speed:").pack(side="left", padx=(0, 10))
        self.speed_var = ctk.DoubleVar(value=1.0)
        ctk.CTkSlider(effects_options_frame, from_=0.5, to=2.0, variable=self.speed_var).pack(side="left")

        # Action button
        apply_effects_button = ctk.CTkButton(effects_frame, text="Apply Effects", command=self.apply_effects)
        apply_effects_button.pack(pady=10)
        
        # Vocal Remover Section
        vocal_remover_frame = ctk.CTkFrame(tools_frame)
        vocal_remover_frame.pack(fill="x", pady=20)
        
        vocal_remover_label = ctk.CTkLabel(vocal_remover_frame, text="Vocal Remover", font=ctk.CTkFont(size=16, weight="bold"))
        vocal_remover_label.pack(anchor="w", padx=10, pady=10)

        # File selection
        remover_file_frame = ctk.CTkFrame(vocal_remover_frame)
        remover_file_frame.pack(fill="x", padx=10, pady=(0,10))
        self.remover_filepath_var = ctk.StringVar()
        remover_file_entry = ctk.CTkEntry(remover_file_frame, textvariable=self.remover_filepath_var, placeholder_text="Select an audio file to remove vocals", state="disabled")
        remover_file_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        remover_select_button = ctk.CTkButton(remover_file_frame, text="Browse", command=self.select_remover_file)
        remover_select_button.pack(side="left")

        # Action button
        remove_vocals_button = ctk.CTkButton(vocal_remover_frame, text="Remove Vocals", command=self.remove_vocals)
        remove_vocals_button.pack(pady=10)

    def setup_metadata_tab(self):
        metadata_frame = ctk.CTkFrame(self.metadata_tab, fg_color="transparent")
        metadata_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # File selection
        metadata_file_frame = ctk.CTkFrame(metadata_frame)
        metadata_file_frame.pack(fill="x", pady=(0, 20))
        self.metadata_filepath_var = ctk.StringVar()
        metadata_file_entry = ctk.CTkEntry(metadata_file_frame, textvariable=self.metadata_filepath_var, placeholder_text="Select an audio file to edit metadata", state="disabled")
        metadata_file_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        metadata_select_button = ctk.CTkButton(metadata_file_frame, text="Browse", command=self.select_metadata_file)
        metadata_select_button.pack(side="left")

        # Metadata fields
        metadata_fields_frame = ctk.CTkFrame(metadata_frame)
        metadata_fields_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(metadata_fields_frame, text="Title:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.title_var = ctk.StringVar()
        ctk.CTkEntry(metadata_fields_frame, textvariable=self.title_var).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        ctk.CTkLabel(metadata_fields_frame, text="Artist:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.artist_var = ctk.StringVar()
        ctk.CTkEntry(metadata_fields_frame, textvariable=self.artist_var).grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(metadata_fields_frame, text="Album:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.album_var = ctk.StringVar()
        ctk.CTkEntry(metadata_fields_frame, textvariable=self.album_var).grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(metadata_fields_frame, text="Genre:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.genre_var = ctk.StringVar()
        ctk.CTkEntry(metadata_fields_frame, textvariable=self.genre_var).grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        
        metadata_fields_frame.columnconfigure(1, weight=1)

        # Action button
        save_metadata_button = ctk.CTkButton(metadata_frame, text="Save Metadata", command=self.save_metadata)
        save_metadata_button.pack(pady=10)

    def select_metadata_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("MP3 files", "*.mp3"), ("All files", "*.*")])
        if filepath:
            self.metadata_filepath_var.set(filepath)
            self.load_metadata(filepath)

    def load_metadata(self, filepath):
        try:
            audio = EasyID3(filepath)
            self.title_var.set(audio.get('title', [''])[0])
            self.artist_var.set(audio.get('artist', [''])[0])
            self.album_var.set(audio.get('album', [''])[0])
            self.genre_var.set(audio.get('genre', [''])[0])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load metadata: {e}")

    def save_metadata(self):
        filepath = self.metadata_filepath_var.get()
        if not filepath or not os.path.exists(filepath):
            messagebox.showerror("Error", "Please select a valid audio file.")
            return

        try:
            audio = EasyID3(filepath)
            audio['title'] = self.title_var.get()
            audio['artist'] = self.artist_var.get()
            audio['album'] = self.album_var.get()
            audio['genre'] = self.genre_var.get()
            audio.save()
            messagebox.showinfo("Success", "Metadata saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save metadata: {e}")


    def select_remover_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav *.mp3 *.m4a"), ("All files", "*.*")])
        if filepath:
            self.remover_filepath_var.set(filepath)

    def remove_vocals(self):
        filepath = self.remover_filepath_var.get()
        if not filepath or not os.path.exists(filepath):
            messagebox.showerror("Error", "Please select a valid audio file.")
            return

        save_path = filedialog.asksaveasfilename(
            title="Save Instrumental File",
            defaultextension=".mp3",
            filetypes=(("MP3 files", "*.mp3"), ("WAV files", "*.wav"), ("All files", "*.*"))
        )
        if not save_path:
            return

        self.show_loading()
        threading.Thread(target=self._remove_vocals_thread, args=(filepath, save_path), daemon=True).start()

    def _remove_vocals_thread(self, filepath, save_path):
        try:
            from pydub import AudioSegment

            audio = AudioSegment.from_file(filepath)
            
            # This is a simplified vocal removal technique (phase inversion).
            # It works best on stereo tracks where vocals are panned to the center.
            if audio.channels == 2:
                left, right = audio.split_to_mono()
                inverted_right = right.invert_phase()
                mono_sum = left.overlay(inverted_right)
                instrumental = mono_sum
            else:
                # Cannot process mono audio this way
                messagebox.showwarning("Warning", "Vocal removal works best on stereo tracks. This is a mono file.")
                instrumental = audio

            output_format = os.path.splitext(save_path)[1][1:].lower()
            instrumental.export(save_path, format=output_format)
            messagebox.showinfo("Success", f"Instrumental track saved to {save_path}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove vocals: {e}")
        finally:
            self.hide_loading()

    def select_effects_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav *.mp3 *.m4a"), ("All files", "*.*")])
        if filepath:
            self.effects_filepath_var.set(filepath)

    def apply_effects(self):
        filepath = self.effects_filepath_var.get()
        if not filepath or not os.path.exists(filepath):
            messagebox.showerror("Error", "Please select a valid audio file.")
            return

        save_path = filedialog.asksaveasfilename(
            title="Save Effected File",
            defaultextension=".mp3",
            filetypes=(("MP3 files", "*.mp3"), ("WAV files", "*.wav"), ("All files", "*.*"))
        )
        if not save_path:
            return

        self.show_loading()
        threading.Thread(target=self._apply_effects_thread, args=(filepath, save_path), daemon=True).start()

    def _apply_effects_thread(self, filepath, save_path):
        try:
            from pydub import AudioSegment
            from pydub.effects import low_pass_filter

            audio = AudioSegment.from_file(filepath)

            if self.bass_boost_var.get():
                audio = low_pass_filter(audio, 150)

            if self.reverb_var.get():
                # Pydub doesn't have a built-in reverb. This is a simplified simulation.
                # A more advanced solution would use another library like pysox.
                audio = audio.fade_in(200).fade_out(200)

            if self.reverse_var.get():
                audio = audio.reverse()

            speed = self.speed_var.get()
            if speed != 1.0:
                audio = audio.speedup(playback_speed=speed)

            output_format = os.path.splitext(save_path)[1][1:].lower()
            audio.export(save_path, format=output_format)
            messagebox.showinfo("Success", f"Effects applied and file saved to {save_path}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply effects: {e}")
        finally:
            self.hide_loading()

    def toggle_split_options(self):
        if self.split_method_var.get() == "silence":
            self.split_time_frame.pack_forget()
            self.split_silence_frame.pack(fill="x", pady=(10,0))
        else:
            self.split_silence_frame.pack_forget()
            self.split_time_frame.pack(fill="x", pady=(10,0))

    def select_split_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav *.mp3 *.m4a"), ("All files", "*.*")])
        if filepath:
            self.split_filepath_var.set(filepath)

    def split_file(self):
        filepath = self.split_filepath_var.get()
        if not filepath or not os.path.exists(filepath):
            messagebox.showerror("Error", "Please select a valid audio file.")
            return

        output_dir = filedialog.askdirectory(title="Select Output Folder for Split Files")
        if not output_dir:
            return
            
        self.show_loading()
        threading.Thread(target=self._split_file_thread, args=(filepath, output_dir), daemon=True).start()

    def _split_file_thread(self, filepath, output_dir):
        try:
            from pydub import AudioSegment
            from pydub.silence import split_on_silence

            audio = AudioSegment.from_file(filepath)
            
            if self.split_method_var.get() == "silence":
                min_silence_len = int(self.min_silence_len_var.get())
                silence_thresh = int(self.silence_thresh_var.get())
                chunks = split_on_silence(audio, min_silence_len=min_silence_len, silence_thresh=silence_thresh, keep_silence=200)
            else: # Split by time
                duration_s = int(self.split_duration_var.get())
                duration_ms = duration_s * 1000
                chunks = [audio[i:i+duration_ms] for i in range(0, len(audio), duration_ms)]

            base_filename = os.path.splitext(os.path.basename(filepath))[0]
            output_format = os.path.splitext(filepath)[1][1:].lower()

            for i, chunk in enumerate(chunks):
                chunk_name = f"{base_filename}_chunk{i}.{output_format}"
                chunk.export(os.path.join(output_dir, chunk_name), format=output_format)

            messagebox.showinfo("Success", f"Audio split into {len(chunks)} chunks in {output_dir}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to split file: {e}")
        finally:
            self.hide_loading()

    def add_merge_files(self):
        filepaths = filedialog.askopenfilenames(
            title="Select Audio Files to Merge",
            filetypes=(
                ("Audio files", "*.mp3 *.wav *.ogg *.m4a *.flac"),
                ("All files", "*.*")
            )
        )
        if filepaths:
            for f in filepaths:
                self.merge_listbox.insert(END, f)
    
    def remove_merge_files(self):
        selected_indices = self.merge_listbox.curselection()
        for i in reversed(selected_indices):
            self.merge_listbox.delete(i)

    def merge_files(self):
        files_to_merge = self.merge_listbox.get(0, END)
        if len(files_to_merge) < 2:
            messagebox.showerror("Error", "Please select at least two files to merge.")
            return

        save_path = filedialog.asksaveasfilename(
            title="Save Merged File",
            defaultextension=".mp3",
            filetypes=(("MP3 files", "*.mp3"), ("WAV files", "*.wav"), ("All files", "*.*"))
        )
        if not save_path:
            return

        self.show_loading()
        threading.Thread(target=self._merge_files_thread, args=(files_to_merge, save_path), daemon=True).start()

    def _merge_files_thread(self, files_to_merge, save_path):
        try:
            from pydub import AudioSegment
            
            combined = AudioSegment.empty()
            for filepath in files_to_merge:
                sound = AudioSegment.from_file(filepath)
                combined += sound

            output_format = os.path.splitext(save_path)[1][1:].lower()
            combined.export(save_path, format=output_format)
            messagebox.showinfo("Success", f"Files merged successfully and saved to {save_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to merge files: {e}")
        finally:
            self.hide_loading()


    def start_recording(self):
        self.record_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.save_rec_button.configure(state="disabled")
        self.transcribe_rec_button.configure(state="disabled")
        self.post_rec_frame.pack_forget()

        self.is_recording = True
        self.recording_status_var.set("Status: Recording...")
        self.audio_frames = []
        
        self.pyaudio_instance = pyaudio.PyAudio()
        self.audio_stream = self.pyaudio_instance.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024, stream_callback=self.audio_callback)
        self.audio_stream.start_stream()

    def stop_recording(self):
        if not self.is_recording:
            return
            
        self.is_recording = False
        self.recording_status_var.set("Status: Stopped")
        
        self.audio_stream.stop_stream()
        self.audio_stream.close()
        self.pyaudio_instance.terminate()

        self.record_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.save_rec_button.configure(state="normal")
        self.transcribe_rec_button.configure(state="normal")
        self.post_rec_frame.pack(pady=10)

        # Save to a temporary file
        self.recorded_audio_path = "temp_recording.wav"
        with wave.open(self.recorded_audio_path, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(self.pyaudio_instance.get_sample_size(pyaudio.paInt16))
            wf.setframerate(44100)
            wf.writeframes(b''.join(self.audio_frames))

    def audio_callback(self, in_data, frame_count, time_info, status):
        if self.is_recording:
            self.audio_frames.append(in_data)
        return (in_data, pyaudio.paContinue)

    def save_recording(self):
        if self.recorded_audio_path and os.path.exists(self.recorded_audio_path):
            save_path = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV files", "*.wav"), ("MP3 files", "*.mp3"), ("All files", "*.*")])
            if save_path:
                # If saving as MP3, we need to convert it
                if save_path.lower().endswith(".mp3"):
                    audio = AudioSegment.from_wav(self.recorded_audio_path)
                    audio.export(save_path, format="mp3")
                else:
                    import shutil
                    shutil.copy(self.recorded_audio_path, save_path)
                messagebox.showinfo("Success", f"Recording saved to {save_path}")
        else:
            messagebox.showerror("Error", "No recording to save.")
            
    def transcribe_recording(self):
        if self.recorded_audio_path and os.path.exists(self.recorded_audio_path):
            self.stt_filepath_var.set(self.recorded_audio_path)
            self.start_transcription()
            self.tab_view.set("Speech to Text") # Switch to STT tab
        else:
            messagebox.showerror("Error", "No recording to transcribe.")

    def convert_to_speech(self):
        text = self.tts_text.get("1.0", "end-1c")
        if not text:
            messagebox.showerror("Error", "Please enter some text.")
            return

        selected_voice_id = self.voice_map[self.tts_voice_var.get()]

        self.show_loading()
        threading.Thread(target=self._convert_to_speech_thread, args=(text, selected_voice_id), daemon=True).start()

    def _convert_to_speech_thread(self, text, voice_id):
        try:
            self.tts_button.configure(state="disabled")

            self.tts_engine.setProperty('voice', voice_id)
            # Save as WAV to avoid potential MP3 corruption issues with pygame
            self.tts_audio_path = "temp_tts.wav"
            self.tts_engine.save_to_file(text, self.tts_audio_path)
            self.tts_engine.runAndWait()

            self.play_button.configure(state="normal")
            self.save_button.configure(state="normal")
            messagebox.showinfo("Success", "Text converted to speech.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to convert text to speech:\n{e}")
        finally:
            self.tts_button.configure(state="normal")
            self.hide_loading()

    def play_speech(self):
        if self.tts_audio_path and os.path.exists(self.tts_audio_path):
            pygame.mixer.music.load(self.tts_audio_path)
            pygame.mixer.music.play()
        else:
            messagebox.showerror("Error", "No audio to play.")

    def save_speech(self):
        if self.tts_audio_path and os.path.exists(self.tts_audio_path):
            save_path = filedialog.asksaveasfilename(
                defaultextension=".wav",
                filetypes=[("WAV files", "*.wav"), ("MP3 files", "*.mp3"), ("All files", "*.*")]
            )
            if save_path:
                try:
                    if save_path.lower().endswith(".mp3"):
                        # Convert WAV to MP3 for saving
                        audio = AudioSegment.from_wav(self.tts_audio_path)
                        audio.export(save_path, format="mp3")
                    else:
                        # Just copy the WAV file
                        import shutil
                        shutil.copy(self.tts_audio_path, save_path)
                    messagebox.showinfo("Success", f"Audio saved to {save_path}")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save file: {e}")
        else:
            messagebox.showerror("Error", "No audio to save.")

    def select_stt_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav *.mp3 *.m4a"), ("All files", "*.*")])
        if filepath:
            self.stt_filepath_var.set(filepath)
            self.stt_start_button.configure(state="normal")

    def start_transcription(self):
        filepath = self.stt_filepath_var.get()
        if not filepath or not os.path.exists(filepath):
            messagebox.showerror("Error", "Please select a valid audio file.")
            return

        self.show_loading()
        threading.Thread(target=self._start_transcription_thread, args=(filepath,), daemon=True).start()

    def _start_transcription_thread(self, filepath):
        try:
            # This is a placeholder for model loading. In a real app, you'd want to
            # manage model downloads and selection more gracefully.
            model_path = "vosk-model-small-en-us-0.15" # Example model path
            if not os.path.exists(model_path):
                messagebox.showerror("Error", f"Vosk model not found at {model_path}. Please download it.")
                self.hide_loading()
                return

            self.stt_start_button.configure(state="disabled")
            self.stt_output.delete("1.0", "end")

            model = Model(model_path)
            
            # Convert to WAV if necessary
            if not filepath.lower().endswith(".wav"):
                wav_path = "temp_stt_input.wav"
                sound = AudioSegment.from_file(filepath)
                sound.export(wav_path, format="wav")
                filepath = wav_path

            wf = wave.open(filepath, "rb")
            if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
                 messagebox.showerror("Error", "Audio file must be WAV format mono PCM.")
                 self.hide_loading()
                 return
            
            rec = KaldiRecognizer(model, wf.getframerate())
            rec.SetWords(True)
            
            # This can be slow, so ideally run in a thread
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    self.stt_output.insert("end", result['text'] + " ")
                else:
                    partial = json.loads(rec.PartialResult())
                    # You can update the UI with partial results here if desired
            
            final_result = json.loads(rec.FinalResult())
            self.stt_output.insert("end", final_result['text'])

            self.stt_save_button.configure(state="normal")
            messagebox.showinfo("Success", "Transcription complete.")

        except Exception as e:
            messagebox.showerror("Error", f"Transcription failed: {e}")
        finally:
            self.stt_start_button.configure(state="normal")
            self.hide_loading()

    def save_transcription(self):
        text = self.stt_output.get("1.0", "end-1c")
        if not text:
            messagebox.showerror("Error", "No transcription to save.")
            return
            
        save_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("SRT files", "*.srt"), ("All files", "*.*")])
        if save_path:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(text)
            messagebox.showinfo("Success", f"Transcription saved to {save_path}")

    def download_youtube_video(self):
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
        self.show_loading()

        threading.Thread(target=self._download_thread, args=(url, download_type, output_path), daemon=True).start()

    def _download_thread(self, url, download_type, output_path):
        try:
            ydl_opts = {
                'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
                'progress_hooks': [self.download_progress_hook],
            }

            if download_type == "audio":
                ydl_opts['format'] = 'bestaudio/best'
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            else:
                ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            messagebox.showinfo("Success", "Download completed successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to download:\n{e}")
        finally:
            self.download_button.configure(state="normal")
            self.download_progress.set(0)
            self.hide_loading()

    def download_progress_hook(self, d):
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
            if total_bytes:
                progress = d['downloaded_bytes'] / total_bytes
                self.download_progress.set(progress)
                self.update_idletasks()
        elif d['status'] == 'finished':
            self.download_progress.set(1)

    def select_files(self):
        filepaths = filedialog.askopenfilenames(
            title="Select Audio Files",
            filetypes=(
                ("Audio files", "*.mp3 *.wav *.ogg *.m4a *.flac"),
                ("All files", "*.*")
            )
        )
        if filepaths:
            self.file_listbox.delete(0, END)
            for f in filepaths:
                self.file_listbox.insert(END, f)
    
    def select_output_folder(self):
        folder_path = filedialog.askdirectory(title="Select Output Folder")
        if folder_path:
            self.output_folder_var.set(folder_path)
            self.same_folder_var.set(False)

    def toggle_output_folder(self):
        if self.same_folder_var.get():
            self.output_folder_var.set("Same folder")
        else:
            self.output_folder_var.set("")

    def start_conversion(self):
        files_to_convert = self.file_listbox.get(0, END)
        if not files_to_convert:
            messagebox.showerror("Error", "No files selected for conversion.")
            return

        output_folder = self.output_folder_var.get()
        if not self.same_folder_var.get() and not os.path.isdir(output_folder):
            messagebox.showerror("Error", "Output folder not found.")
            return

        self.show_loading()
        threading.Thread(target=self._start_conversion_thread, args=(files_to_convert, output_folder), daemon=True).start()

    def _start_conversion_thread(self, files_to_convert, output_folder):
        total_files = len(files_to_convert)
        self.progress_bar.set(0)
        
        try:
            for i, filepath in enumerate(files_to_convert):
                original_dir = os.path.dirname(filepath)
                filename = os.path.basename(filepath)
                name, _ = os.path.splitext(filename)
                output_format = self.format_var.get().lower()
                
                save_dir = output_folder if not self.same_folder_var.get() else original_dir
                new_filepath = os.path.join(save_dir, f"{name}.{output_format}")

                options = {
                    "format": self.format_var.get(),
                    "bitrate": self.bitrate_var.get(),
                    "trim": {
                        "start": float(self.start_trim_var.get()) if self.start_trim_var.get() else 0,
                        "end": float(self.end_trim_var.get()) if self.end_trim_var.get() else None,
                    },
                    "volume": self.volume_var.get()
                }

                if self.converter.convert(filepath, new_filepath, options):
                    progress = (i + 1) / total_files
                    self.progress_bar.set(progress)
                    self.update_idletasks() # Force UI update

            messagebox.showinfo("Success", "All files converted successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during conversion: {e}")
        finally:
            self.progress_bar.set(0)
            self.hide_loading() 