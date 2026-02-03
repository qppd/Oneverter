import os
from typing import List, Dict, Any
from .base_converter import BaseConverter
import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
from pdf2docx import Converter as PdfToDocxConverter
from docx2pdf import convert as DocxToPdfConvert
import PyPDF2
from docx import Document
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from ui.animated_spinner import AnimatedSpinner
import platform
import subprocess


class DocumentConverter(BaseConverter):
    """Document converter for PDF, DOCX, TXT files"""
    
    def __init__(self):
        super().__init__()
        self.name = "Document Converter"
        self.description = "Convert between PDF, DOCX, and TXT formats"
        self.icon = "📄"
        
    def get_supported_formats(self) -> List[str]:
        # Overriding to return a concrete list
        return ['.pdf', '.docx', '.txt']
    
    def convert(self, input_path: str, output_path: str, options: Dict[str, Any] = None) -> bool:
        """Convert document files"""
        try:
            input_ext = os.path.splitext(input_path)[1].lower()
            output_ext = os.path.splitext(output_path)[1].lower()
            
            # PDF to DOCX
            if input_ext == '.pdf' and output_ext == '.docx':
                return self._pdf_to_docx(input_path, output_path)
            
            # DOCX to PDF
            elif (input_ext == '.docx' or input_ext == '.doc') and output_ext == '.pdf':
                return self._docx_to_pdf(input_path, output_path)
            
            # PDF to TXT
            elif input_ext == '.pdf' and output_ext == '.txt':
                return self._pdf_to_txt(input_path, output_path)
            
            # DOCX to TXT
            elif (input_ext == '.docx' or input_ext == '.doc') and output_ext == '.txt':
                return self._docx_to_txt(input_path, output_path)
            
            # TXT to PDF
            elif input_ext == '.txt' and output_ext == '.pdf':
                return self._txt_to_pdf(input_path, output_path)
            
            else:
                print(f"Unsupported conversion: {input_ext} to {output_ext}")
                return False
                
        except Exception as e:
            print(f"Error in document conversion: {e}")
            return False
    
    def _pdf_to_docx(self, input_path: str, output_path: str) -> bool:
        """Convert PDF to DOCX using pdf2docx."""
        try:
            cv = PdfToDocxConverter(input_path)
            cv.convert(output_path, start=0, end=None)
            cv.close()
            return True
        except Exception as e:
            print(f"Error converting PDF to DOCX: {e}")
            return False
    
    def _docx_to_pdf(self, input_path: str, output_path: str) -> bool:
        """Convert DOCX to PDF using docx2pdf."""
        try:
            DocxToPdfConvert(input_path, output_path)
            return True
        except Exception as e:
            # docx2pdf can be slow or fail on complex docs, handle gracefully
            print(f"Error converting DOCX to PDF: {e}")
            return False
    
    def _pdf_to_txt(self, input_path: str, output_path: str) -> bool:
        """Extract text from PDF using PyPDF2."""
        try:
            with open(input_path, 'rb') as pdf_file:
                reader = PyPDF2.PdfReader(pdf_file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            
            with open(output_path, 'w', encoding='utf-8') as txt_file:
                txt_file.write(text)
            return True
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return False
    
    def _docx_to_txt(self, input_path: str, output_path: str) -> bool:
        """Extract text from DOCX using python-docx."""
        try:
            doc = Document(input_path)
            text = "\n".join([para.text for para in doc.paragraphs])
            
            with open(output_path, 'w', encoding='utf-8') as txt_file:
                txt_file.write(text)
            return True
        except Exception as e:
            print(f"Error extracting text from DOCX: {e}")
            return False
    
    def _txt_to_pdf(self, input_path: str, output_path: str) -> bool:
        """Convert TXT to PDF using reportlab."""
        try:
            with open(input_path, 'r', encoding='utf-8') as txt_file:
                lines = txt_file.readlines()

            c = canvas.Canvas(output_path, pagesize=letter)
            width, height = letter
            y = height - 40
            
            for line in lines:
                if y < 40: # Create a new page if there's no space left
                    c.showPage()
                    y = height - 40
                c.drawString(40, y, line.strip())
                y -= 14 # Move to the next line
            
            c.save()
            return True
        except Exception as e:
            print(f"Error converting TXT to PDF: {e}")
            return False


class DocumentConverterUI:
    """UI for document converter. Builds UI components inside a parent frame."""
    
    def __init__(self, parent_frame: ctk.CTkFrame):
        self.parent = parent_frame
        self.converter = DocumentConverter()
        self.input_files = []
        self.output_dir = ""
        self.input_widgets = [] # To easily disable/enable them
        
        # The create_ui logic is now directly in __init__
        self._build_ui()
        
    def _build_ui(self):
        """Create the document converter UI within the parent frame."""
        # The main container is now the parent_frame itself.
        # Configure the parent frame's grid
        self.parent.grid_rowconfigure(2, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)

        # File selection
        file_frame = ctk.CTkFrame(self.parent)
        file_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        file_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(file_frame, text="1. Select Files", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, padx=5, pady=(5, 2), sticky="w")
        
        self.file_listbox = ctk.CTkTextbox(file_frame, height=80)
        self.file_listbox.grid(row=1, column=0, padx=5, pady=2, sticky="ew")
        
        button_frame = ctk.CTkFrame(file_frame, fg_color="transparent")
        button_frame.grid(row=2, column=0, padx=5, pady=2, sticky="w")
        
        browse_button = ctk.CTkButton(
            button_frame, text="📁 Browse Files", command=self.browse_files
        )
        browse_button.grid(row=0, column=0, padx=0)
        self.input_widgets.append(browse_button)
        
        clear_button = ctk.CTkButton(
            button_frame, text="🗑️ Clear", command=self.clear_files
        )
        clear_button.grid(row=0, column=1, padx=2)
        self.input_widgets.append(clear_button)
        
        # Output directory
        output_frame = ctk.CTkFrame(self.parent)
        output_frame.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        
        ctk.CTkLabel(output_frame, text="2. Choose Output Location", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, padx=5, pady=(5, 2), sticky="w")
        
        self.output_label = ctk.CTkLabel(output_frame, text="No directory selected.", text_color="gray", wraplength=300, justify="left")
        self.output_label.grid(row=1, column=0, padx=5, pady=2, sticky="w")
        
        output_button = ctk.CTkButton(
            output_frame, text="📂 Select Folder", command=self.browse_output_dir
        )
        output_button.grid(row=2, column=0, padx=5, pady=(2, 5), sticky="w")
        self.input_widgets.append(output_button)
        
        # Conversion options & action
        action_frame = ctk.CTkFrame(self.parent)
        action_frame.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")
        action_frame.grid_columnconfigure(0, weight=1)
        action_frame.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(action_frame, text="3. Configure & Convert", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, padx=5, pady=(5,2), sticky="w")
        
        # Target format selection
        format_frame = ctk.CTkFrame(action_frame, fg_color="transparent")
        format_frame.grid(row=1, column=0, padx=5, pady=2, sticky="w")
        
        ctk.CTkLabel(format_frame, text="Target Format:").grid(row=0, column=0, padx=0)
        
        self.format_var = ctk.StringVar(value="docx")
        self.format_menu = ctk.CTkOptionMenu(
            format_frame, values=["docx", "pdf", "txt"], variable=self.format_var
        )
        self.format_menu.grid(row=0, column=1, padx=5)
        self.input_widgets.append(self.format_menu)
        
        # Convert button
        self.convert_button = ctk.CTkButton(
            action_frame, text="🚀 Start Conversion", 
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.start_conversion
        )
        self.convert_button.grid(row=2, column=0, padx=5, pady=10)
        self.input_widgets.append(self.convert_button)
        
        # --- Progress Area ---
        progress_area = ctk.CTkFrame(action_frame, fg_color="transparent")
        progress_area.grid(row=3, column=0, sticky="sew", padx=5, pady=5)
        progress_area.grid_columnconfigure(0, weight=1)
        
        self.progress_bar = ctk.CTkProgressBar(progress_area)
        self.progress_bar.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        self.progress_bar.set(0)
        
        self.status_label = ctk.CTkLabel(progress_area, text="Ready", text_color="gray")
        self.status_label.grid(row=1, column=0, sticky="w")

        # --- Loading Overlay and Spinner ---
        self.overlay = ctk.CTkFrame(self.parent, fg_color="black")
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.overlay.lower() # Hide it initially
        
        self.spinner = AnimatedSpinner(self.overlay, path_to_gif="assets/loading_spinner.gif", size=(200, 200))

    def _set_ui_state_converting(self):
        """Disable inputs and show the loading animation."""
        # Use a solid, dark color for the overlay. This is a valid hex code.
        self.overlay.configure(fg_color=("#606060", "#202020"))
        self.overlay.lift()
        self.spinner.show()
        for widget in self.input_widgets:
            widget.configure(state="disabled")

    def _set_ui_state_idle(self):
        """Enable inputs and hide the loading animation."""
        self.spinner.hide()
        self.overlay.lower()
        for widget in self.input_widgets:
            widget.configure(state="normal")
            
    def browse_files(self):
        """Browse for input files and update the UI."""
        files = filedialog.askopenfilenames(
            title="Select Document Files",
            filetypes=[
                ("Supported Files", "*.pdf *.docx *.doc *.txt"),
                ("PDF", "*.pdf"),
                ("Word Document", "*.docx *.doc"),
                ("Text File", "*.txt")
            ]
        )
        
        if files:
            self.input_files.extend(list(files))
            self.update_file_list()
            self._update_format_options() # Update dropdown based on selection
    
    def clear_files(self):
        """Clear selected files"""
        self.input_files = []
        self.file_listbox.configure(state="normal")
        self.file_listbox.delete("1.0", "end")
        self.file_listbox.configure(state="disabled")
    
    def update_file_list(self):
        """Update the file list display"""
        self.file_listbox.configure(state="normal")
        self.file_listbox.delete("1.0", "end")
        if not self.input_files:
            self.file_listbox.insert("end", "No files selected.")
        else:
            for file in self.input_files:
                self.file_listbox.insert("end", f"• {os.path.basename(file)}\n")
        self.file_listbox.configure(state="disabled")
    
    def _update_format_options(self):
        """Dynamically update the target format dropdown based on selected files."""
        if not self.input_files:
            self.format_menu.configure(values=["docx", "pdf", "txt"])
            return

        # Get all unique extensions from the input files
        input_extensions = {os.path.splitext(f)[1].lower().replace('.', '') for f in self.input_files}
        
        # Define all possible target formats
        all_formats = ["docx", "pdf", "txt"]
        
        # If there's only one type of file selected, remove it from the targets
        if len(input_extensions) == 1:
            ext_to_remove = input_extensions.pop()
            if ext_to_remove == "doc": ext_to_remove = "docx" # Treat doc as docx
            
            valid_targets = [f for f in all_formats if f != ext_to_remove]
            self.format_menu.configure(values=valid_targets)
            
            # If the current selection is no longer valid, switch to the first valid one
            if self.format_var.get() not in valid_targets and valid_targets:
                self.format_var.set(valid_targets[0])
        else:
            # If multiple types are selected, all targets are potentially valid
            self.format_menu.configure(values=all_formats)

    def browse_output_dir(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir = directory
            self.output_label.configure(text=f"Output Path: {self.output_dir}")
    
    def start_conversion(self):
        """Start the conversion process"""
        if not self.input_files:
            messagebox.showwarning("Warning", "Please select input files first!")
            return
        
        if not self.output_dir:
            messagebox.showwarning("Warning", "Please select output directory first!")
            return
        
        # Start conversion in a separate thread
        thread = threading.Thread(target=self._convert_files)
        thread.daemon = True
        thread.start()
    
    def _convert_files(self):
        """Convert files in background thread with UI state changes."""
        try:
            # Set UI to "converting" state
            self.parent.after(0, self._set_ui_state_converting)
            
            self.status_label.configure(text="Preparing...")
            
            target_format = self.format_var.get()
            total_files = len(self.input_files)
            
            for i, input_file in enumerate(self.input_files):
                # Update progress
                progress = (i + 1) / total_files
                self.progress_bar.set(progress)
                
                # Update status
                self.status_label.configure(text=f"({i+1}/{total_files}) Converting {os.path.basename(input_file)}...")
                
                # Convert file
                output_filename = self.converter.get_output_filename(input_file, target_format) # No longer need the extra dot
                output_path = os.path.join(self.output_dir, output_filename)
                
                # Skip conversion if source and target extensions are the same
                input_ext = os.path.splitext(input_file)[1].lower().replace('.', '')
                target_ext = target_format.lower()
                if (input_ext == target_ext) or (input_ext == 'doc' and target_ext == 'docx'):
                    print(f"Skipping {os.path.basename(input_file)}: Same input and output format.")
                    continue

                success = self.converter.convert(input_file, output_path)
                
                if not success:
                    print(f"Failed to convert {input_file}")
            
            # Conversion complete
            self.status_label.configure(text=f"Conversion of {total_files} files complete!")
            self.progress_bar.set(1.0)
            
            # Ask user to open output folder
            if messagebox.askyesno("Success", f"Converted {len(self.input_files)} files successfully!\n\nDo you want to open the output folder?"):
                self._open_output_folder()
            
        except Exception as e:
            self.status_label.configure(text=f"Error: {str(e)}", text_color="red")
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
        finally:
            # Always return UI to "idle" state
            self.parent.after(0, self._set_ui_state_idle)

    def _open_output_folder(self):
        """Opens the output directory in the system's file explorer."""
        output_dir = self.output_dir
        if not output_dir or not os.path.isdir(output_dir):
            print(f"Output directory not found or is not a directory: {output_dir}")
            return
            
        try:
            system = platform.system()
            if system == "Windows":
                os.startfile(output_dir)
            elif system == "Darwin": # macOS
                subprocess.run(["open", output_dir], check=True)
            else: # Linux and other Unix-like
                subprocess.run(["xdg-open", output_dir], check=True)
        except Exception as e:
            print(f"Error opening output folder: {e}")
            if self.unified_main_window:
                self.unified_main_window.show_notification(f"Could not open the output folder automatically. Path: {output_dir}", type_="warning")

    def get_conversion_options(self) -> Dict[str, Any]:
        """Get conversion options from UI"""
        return {
            "target_format": self.format_var.get(),
            "output_dir": self.output_dir
        } 