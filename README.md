# Oneverter 🚀

**Your All-in-One Conversion Hub**

Oneverter is a modern, user-friendly desktop application built with Python and CustomTkinter that provides comprehensive file conversion capabilities for everyday use.

## ✨ Features

### 📄 Document Converters
- **PDF to DOCX** - Convert PDF files to editable Word documents
- **DOCX to PDF** - Convert Word documents to PDF format
- **PDF to TXT** - Extract text from PDF files
- **DOCX to TXT** - Convert Word docs to plain text
- **TXT to PDF** - Convert text files to PDF

### 🖼️ Image Converters (Coming Soon)
- Image format conversion (JPG ↔ PNG ↔ WEBP ↔ GIF)
- Image resizing and compression
- Background removal using AI
- Batch image processing

### 🎥 Video Converters (Coming Soon)
- Video format conversion (MP4 ↔ AVI ↔ MOV ↔ MKV)
- Video to image extraction
- Video compression and trimming

### 🎵 Audio Converters (Coming Soon)
- Audio format conversion (MP3 ↔ WAV ↔ FLAC ↔ AAC)
- Audio extraction from video files
- Audio compression

### 📦 Archive Converters (Coming Soon)
- Archive format conversion (ZIP ↔ RAR ↔ 7Z)
- Archive extraction and creation

### 📊 Data Converters (Coming Soon)
- CSV ↔ Excel conversion
- JSON ↔ XML conversion
- Data format transformation

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup
1. Clone the repository:
```bash
git clone <repository-url>
cd Oneverter
```

2. Create a virtual environment (recommended):
```bash
python -m venv .venv
```

3. Activate the virtual environment:
```bash
# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

## 🚀 Usage

1.  Make sure your virtual environment is activated.

2.  Run the application directly:
```bash
python main.py
```

*Alternatively, you can use the auto-start script which attempts to activate the environment and run the app for you:*
```bash
python auto_start.py
```

3. Click "🚀 Start Conversion" on the main screen.

4. Choose your converter category.

5. For the Document Converter, select your files, choose options, and start converting! Other converters are placeholders for now.

## 📁 Project Structure

```
Oneverter/
├── main.py                     # Main application entry point
├── auto_start.py               # Helper script to run the app
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
│
├── assets/                     # Images and resources
│   ├── main_bg.png
│   └── main_logo.png
│
├── converters/                 # Modules for conversion LOGIC and UI building
│   ├── __init__.py
│   ├── base_converter.py
│   ├── document_converter.py     # Contains DocumentConverter and DocumentConverterUI
│   ├── image_converter.py        # (UI Placeholder)
│   ├── video_converter.py        # (UI Placeholder)
│   ├── audio_converter.py        # (UI Placeholder)
│   ├── archive_converter.py      # (UI Placeholder)
│   └── data_converter.py         # (UI Placeholder)
│
├── ui/                         # WINDOW classes that host the UI
│   ├── __init__.py
│   ├── base_window.py            # Base classes for all windows (BaseMainApp, BaseWindow)
│   ├── converter_window.py       # Main hub for selecting a converter
│   ├── document_converter_window.py # Window for the document converter
│   ├── image_converter_window.py
│   ├── video_converter_window.py
│   ├── audio_converter_window.py
│   ├── archive_converter_window.py
│   └── data_converter_window.py
│
└── utils/                      # Utility functions
    ├── __init__.py
    └── file_utils.py
```

## 🔧 Development

### Adding New Converters

1.  **Create the Logic:** Create a new `..._converter.py` file in the `converters/` directory. Inside, create a `...Converter` class that handles the file conversion logic.
2.  **Create the UI:** In the same file, create a `...ConverterUI` class. This class will take a parent frame and build all the necessary `customtkinter` widgets inside it.
3.  **Create the Window:** Create a new `..._converter_window.py` file in the `ui/` directory. This window class should inherit from `BaseWindow` and its only job is to host the UI you created in the step above.
4.  **Wire it up:** Add the new converter's details and window class to the `categories` list in `ui/converter_window.py`.

### Example Converter Structure:
```python
from converters.base_converter import BaseConverter

class MyConverter(BaseConverter):
    def __init__(self):
        super().__init__()
        self.name = "My Converter"
        self.description = "Convert my files"
        self.icon = "🔧"
        self.supported_formats = ['.ext1', '.ext2']
    
    def convert(self, input_path, output_path, options=None):
        # Your conversion logic here
        pass
    
    def get_supported_formats(self):
        return self.supported_formats
```

## 📋 Dependencies

### Core Dependencies
- `customtkinter` - Modern GUI framework
- `Pillow` - Image processing

### Future Dependencies (commented in requirements.txt)
- `pdf2docx` - PDF to DOCX conversion
- `python-docx` - Word document handling
- `PyPDF2` - PDF processing
- `opencv-python` - Video processing
- `moviepy` - Video editing
- `pydub` - Audio processing
- `rembg` - Background removal
- `pandas` - Data processing

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