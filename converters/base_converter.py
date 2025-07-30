import os
from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseConverter(ABC):
    """Base class for all converters in Oneverter."""
    
    def __init__(self):
        self.supported_formats: List[str] = []
        self.name: str = "Base Converter"
        self.description: str = "Base converter class"
        self.icon: str = "📄"
        
    @abstractmethod
    def convert(self, input_path: str, output_path: str, options: Dict[str, Any] = None) -> bool:
        """Convert a single file."""
        pass
    
    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """Return a list of supported input file extensions (e.g., ['.pdf', '.docx'])."""
        pass
    
    def validate_input_file(self, file_path: str) -> bool:
        """Validate if the input file exists and has a supported extension."""
        if not os.path.exists(file_path):
            return False
        
        file_ext = os.path.splitext(file_path)[1].lower()
        return file_ext in self.get_supported_formats()
    
    def get_output_filename(self, input_path: str, target_format: str) -> str:
        """
        Generate an output filename based on the input path and target format.
        Ensures the target format starts with a dot.
        """
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        # Ensure target_format starts with a dot
        if not target_format.startswith('.'):
            target_format = '.' + target_format
        return f"{base_name}_converted{target_format}" 