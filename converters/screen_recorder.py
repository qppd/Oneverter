import customtkinter as ctk
from tkinter import messagebox
import os
import cv2
import pyautogui
import numpy as np
from threading import Thread, Event
import sounddevice as sd
import wave
import time
from tkinter import filedialog

class ScreenRecorder:
    def __init__(self):
        self.is_recording = False
        self.stop_event = Event()
        self.audio_frames = []

    def _record_audio(self, samplerate, channels):
        self.audio_frames = []
        with sd.InputStream(samplerate=samplerate, channels=channels, callback=self.audio_callback):
            self.stop_event.wait() 

    def audio_callback(self, indata, frames, time, status):
        if status:
            print(status)
        self.audio_frames.append(indata.copy())

    def start(self, output_path, with_audio=False):
        self.is_recording = True
        self.stop_event.clear()
        
        screen_size = pyautogui.size()
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        self.video_writer = cv2.VideoWriter(output_path, fourcc, 20.0, (screen_size.width, screen_size.height))

        if with_audio:
            self.audio_thread = Thread(target=self._record_audio, args=(44100, 2))
            self.audio_thread.start()

        while not self.stop_event.is_set():
            img = pyautogui.screenshot()
            frame = np.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.video_writer.write(frame)
            time.sleep(1/20) # 20 fps

        self.video_writer.release()
        
        if with_audio:
            self.stop_audio(output_path)

    def stop_audio(self, video_path):
        if hasattr(self, 'audio_thread') and self.audio_thread.is_alive():
            self.stop_event.set()
            self.audio_thread.join()

            audio_filename = os.path.splitext(video_path)[0] + ".wav"
            with wave.open(audio_filename, 'wb') as wf:
                wf.setnchannels(2)
                wf.setsampwidth(sd.get_samplerate() // 8) # sample width in bytes
                wf.setframerate(44100)
                wf.writeframes(b''.join(self.audio_frames))
            
            # Here you would typically merge the audio and video files using a library like moviepy
            print(f"Audio saved to {audio_filename}. Merging with video is the next step.")


    def stop(self):
        if self.is_recording:
            self.stop_event.set()
            self.is_recording = False

class ScreenRecorderUI:
    def __init__(self, parent):
        self.parent = parent
        self.recorder = ScreenRecorder()
        self.setup_ui()

    def setup_ui(self):
        main_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.record_button = ctk.CTkButton(main_frame, text="Start Recording", command=self.toggle_recording)
        self.record_button.pack(pady=20)
        
        self.audio_var = ctk.BooleanVar()
        ctk.CTkCheckBox(main_frame, text="Record with Audio", variable=self.audio_var).pack(pady=10)

        self.status_label = ctk.CTkLabel(main_frame, text="Status: Idle")
        self.status_label.pack(pady=10)

    def toggle_recording(self):
        if not self.recorder.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        output_path = filedialog.asksaveasfilename(defaultextension=".avi", title="Save Recording As...")
        if not output_path:
            return

        with_audio = self.audio_var.get()
        self.record_thread = Thread(target=self.recorder.start, args=(output_path, with_audio))
        self.record_thread.start()

        self.record_button.configure(text="Stop Recording")
        self.status_label.configure(text="Status: Recording...")

    def stop_recording(self):
        self.recorder.stop()
        self.record_button.configure(text="Start Recording")
        self.status_label.configure(text="Status: Idle. Processing video...")
        messagebox.showinfo("Success", "Recording stopped.") 