import os
import shutil
from typing import List, Tuple
from pathlib import Path
from moviepy import VideoFileClip


def get_app_data_path(file_name: str) -> str:
    """
    Returns the full path to a file in the application's data directory.
    Creates the directory if it doesn't exist.
    """
    # Use APPDATA on Windows, XDG_CONFIG_HOME or .config on Linux/Mac
    if os.name == 'nt':
        app_data_dir = Path(os.getenv('APPDATA')) / 'Oneverter'
    else:
        app_data_dir = Path.home() / '.config' / 'Oneverter'
    
    # Create the directory if it doesn't exist
    app_data_dir.mkdir(parents=True, exist_ok=True)
    
    return str(app_data_dir / file_name)


def get_file_size(file_path: str) -> str:
    """Get human readable file size"""
    size = os.path.getsize(file_path)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"


def get_file_extension(file_path: str) -> str:
    """Get file extension without dot"""
    return Path(file_path).suffix.lower()[1:]


def is_valid_file(file_path: str, allowed_extensions: List[str]) -> bool:
    """Check if file exists and has valid extension"""
    if not os.path.exists(file_path):
        return False
    
    file_ext = get_file_extension(file_path)
    return file_ext in allowed_extensions


def create_output_directory(output_path: str) -> bool:
    """Create output directory if it doesn't exist"""
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        return True
    except Exception as e:
        print(f"Error creating output directory: {e}")
        return False


def get_unique_filename(file_path: str) -> str:
    """Get unique filename if file already exists"""
    if not os.path.exists(file_path):
        return file_path
    
    base_path = Path(file_path)
    counter = 1
    
    while True:
        new_path = base_path.parent / f"{base_path.stem}_{counter}{base_path.suffix}"
        if not new_path.exists():
            return str(new_path)
        counter += 1


def copy_file_with_progress(src: str, dst: str, progress_callback=None) -> bool:
    """Copy file with progress callback"""
    try:
        file_size = os.path.getsize(src)
        
        with open(src, 'rb') as fsrc:
            with open(dst, 'wb') as fdst:
                copied = 0
                while True:
                    buf = fsrc.read(1024 * 1024)  # 1MB chunks
                    if not buf:
                        break
                    fdst.write(buf)
                    copied += len(buf)
                    
                    if progress_callback:
                        progress = copied / file_size
                        progress_callback(progress)
        
        return True
    except Exception as e:
        print(f"Error copying file: {e}")
        return False


def get_files_in_directory(directory: str, extensions: List[str] = None) -> List[str]:
    """Get all files in directory with optional extension filter"""
    files = []
    
    try:
        for root, dirs, filenames in os.walk(directory):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                
                if extensions:
                    file_ext = get_file_extension(file_path)
                    if file_ext in extensions:
                        files.append(file_path)
                else:
                    files.append(file_path)
    
    except Exception as e:
        print(f"Error getting files from directory: {e}")
    
    return files


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human readable string"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def get_file_info(file_path: str) -> dict:
    """Get comprehensive file information"""
    try:
        stat = os.stat(file_path)
        return {
            'name': os.path.basename(file_path),
            'path': file_path,
            'size': get_file_size(file_path),
            'size_bytes': stat.st_size,
            'extension': get_file_extension(file_path),
            'created': stat.st_ctime,
            'modified': stat.st_mtime,
            'accessed': stat.st_atime
        }
    except Exception as e:
        print(f"Error getting file info: {e}")
        return {} 


def get_media_info(file_path: str) -> dict:
    """Get media file information using moviepy"""
    try:
        clip = VideoFileClip(file_path)
        info = {
            'duration': clip.duration,
            'resolution': f"{clip.w}x{clip.h}",
            'fps': clip.fps,
        }
        clip.close()
        return info
    except Exception as e:
        print(f"Error getting media info: {e}")
        return {} 