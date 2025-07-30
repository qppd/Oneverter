import shutil

def is_ffmpeg_installed():
    """Check if ffmpeg is installed and available in the system's PATH."""
    return shutil.which("ffmpeg") is not None 