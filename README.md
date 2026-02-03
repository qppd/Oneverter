# Oneverter 🚀

**Your All-in-One Conversion Hub**

Oneverter is a modern, user-friendly desktop application built with Python and CustomTkinter that provides comprehensive file conversion capabilities for everyday use. It features a unified single-window interface for seamless navigation between different converter tools.

## ✨ Features

### 📄 Document Converter
- **PDF to DOCX** – Convert PDF files to editable Word documents
- **DOCX to PDF** – Convert Word documents to PDF format
- **PDF to TXT** – Extract text from PDF files
- **DOCX to TXT** – Convert Word docs to plain text
- **TXT to PDF** – Convert text files to PDF

### 🖼️ Image Converter
- Image format conversion (JPG, PNG, WEBP, BMP, TIFF)
- Resize, compress, grayscale, flip, rotate images
- Remove background (AI-powered)
- Adjust brightness and contrast

### 🎵 Audio Converter
- Audio format conversion (MP3, WAV, OGG, M4A, FLAC)
- Trim, adjust volume, set bitrate
- YouTube audio/video downloader
- Text-to-Speech (TTS) and Speech-to-Text (STT)
- Voice recorder and metadata editor

### 🎥 Video Tools
A comprehensive suite of tools for all your video editing needs:
- **Video Converter:** Convert between MP4, AVI, WebM, and GIF, with options for resolution, FPS, and codec
- **Trim & Cut:** Easily trim or cut sections of your videos
- **Merge Videos:** Combine multiple video clips into a single file, with an optional fade transition
- **Add/Remove Audio:** Mute, replace, or add a new audio track to your videos
- **Resize & Crop:** Change video dimensions or crop to a specific area
- **Text & Watermark:** Overlay custom text or a logo onto your videos with position and opacity controls
- **Convert to GIF:** Create animated GIFs from your video clips with options for duration and looping
- **Extract Frames:** Save video frames as a sequence of images (PNG/JPG)
- **Subtitle Tool:** Burn subtitles from an SRT file directly into your video
- **Playback Speed:** Change the playback speed of your videos (e.g., 0.5x, 1.5x, 2x)
- **YouTube Downloader:** Download videos from YouTube in various formats and resolutions
- **Screen Recorder:** Record your screen, with an option to include audio from your microphone

### 📦 Archive Converter
- Archive format conversion (ZIP, 7Z, TAR)
- Archive extraction and creation

### 📊 Data Converter
- CSV ↔ Excel conversion
- JSON ↔ XML conversion
- Data format transformation

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- FFmpeg (for video/audio processing)

### Setup
1. Clone the repository:
```bash
git clone https://github.com/qppd/Oneverter.git
cd Oneverter
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

## 🚀 Usage

1. Launch the application using `python main.py`
2. Use the sidebar to navigate between different converter categories
3. Select your files, choose conversion options, and start converting!

## 📁 Project Structure

```
Oneverter/
├── main.py                     # Main application entry point
├── auto_start.py               # Helper script to run the app
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
│
├── assets/                     # Images and resources
│
├── converters/                 # Conversion logic and UI components
│   ├── __init__.py
│   ├── base_converter.py       # Base converter class
│   ├── base_converter_ui.py    # Base UI class
│   ├── document_converter.py
│   ├── image_converter.py
│   ├── audio_converter.py
│   ├── video_converter.py
│   ├── video_trimmer.py
│   ├── video_merger.py
│   ├── video_audio_editor.py
│   ├── video_resizer.py
│   ├── video_watermarker.py
│   ├── video_to_gif_converter.py
│   ├── frame_extractor.py
│   ├── subtitle_tool.py
│   ├── speed_changer.py
│   ├── youtube_downloader.py
│   ├── screen_recorder.py
│   ├── archive_converter.py
│   └── data_converter.py
│   └── __pycache__/
│
├── ui/                         # UI components and windows
│   ├── __init__.py
│   ├── unified_main_window.py  # Main unified interface
│   ├── theme.py                # UI theming and styles
│   ├── base_window.py
│   ├── converter_panel.py      # Base panel class
│   ├── notifications.py
│   ├── animated_spinner.py
│   ├── components/             # Reusable UI components
│   ├── panels/                 # Converter panels
│   └── __pycache__/
│
├── utils/                      # Utility functions
│   ├── __init__.py
│   ├── file_utils.py
│   ├── system_utils.py
│   ├── auth/                   # Authentication utilities (legacy)
│   ├── security/               # Security utilities
│   └── __pycache__/
│
└── tests/                      # Test files
    ├── test_unified_interface.py
    └── ...
```

## 🔧 Development

### Adding New Converters

1. **Create the Logic:** Create a new `..._converter.py` file in the `converters/` directory. Inside, create a `...Converter` class that handles the file conversion logic.

2. **Create the UI:** In the same file, create a `...ConverterUI` class that inherits from `BaseConverterUI` and builds the UI within a parent frame.

3. **Create the Panel:** Create a new `..._converter_panel.py` file in the `ui/panels/` directory. This panel class should inherit from `ConverterPanel` and integrate the UI.

4. **Register the Panel:** Add the new panel to the `PANEL_REGISTRY` in `ui/panels/__init__.py`.

### Example Converter Structure:
```python
from converters.base_converter import BaseConverter
from converters.base_converter_ui import BaseConverterUI

class MyConverter(BaseConverter):
    def __init__(self):
        super().__init__()
        self.name = "My Converter"
        self.description = "Convert my files"
        self.icon = "🔧"
    
    def convert(self, input_path, output_path, options=None):
        # Your conversion logic here
        pass
    
    def get_supported_formats(self):
        return ['.ext1', '.ext2']

class MyConverterUI(BaseConverterUI):
    def __init__(self, parent_frame):
        super().__init__(parent_frame)
        self.converter = MyConverter()
        self.build_ui()
    
    def build_ui(self):
        # Build UI components
        pass
```

## 📋 Dependencies

### Core Dependencies
- `customtkinter` - Modern GUI framework
- `Pillow` - Image processing
- `moviepy` - Video editing and processing
- `pydub` - Audio processing
- `yt-dlp` - YouTube video downloading
- `pysrt` - Subtitle file parsing
- `opencv-python` - Video processing
- `pyautogui` - Screen capture
- `sounddevice` - Audio recording
- `pyaudio` - Audio I/O
- `mutagen` - Audio metadata
- `pdf2docx` - PDF to DOCX conversion
- `docx2pdf` - DOCX to PDF conversion
- `PyPDF2` - PDF processing
- `reportlab` - PDF generation
- `rembg` - Background removal
- `python-docx` - Word document handling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- CustomTkinter team for the amazing GUI framework
- All open-source libraries used in this project
- Contributors and users of Oneverter

## 📞 Support

If you encounter any issues or have questions:
1. Check the documentation
2. Search existing issues
3. Create a new issue with detailed information

---

**Made with ❤️ for the community** 