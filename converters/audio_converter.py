import customtkinter as ctk
from .base_converter import BaseConverter
from pydub import AudioSegment
import os
from tkinter import messagebox


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