import customtkinter as ctk
from converters.archive_converter import ArchiveConverterUI
from ..base_converter_panel import BaseConverterPanel


class ArchiveConverterPanel(BaseConverterPanel):
    def on_back(self):
        self.destroy()
    """Panel for the Archive Converter, for embedding in unified interface."""
    
    def get_title(self) -> str:
        """Get the panel title."""
        return "📦 Archive Converter"
    
    def setup_converter(self):
        """Setup the specific converter UI."""
        self.archive_ui = ArchiveConverterUI(self.content_frame)

    def __init__(self, parent):
        super().__init__(parent)
        self._init_state()
        self._build_ui()

    def _init_state(self):
        self.selected_files = []
        self.selected_format = None
        self.action_type = None
        self.output_dir = None
        self.progress_var = ctk.DoubleVar(value=0)
        self.status_var = ctk.StringVar(value="Ready")

    def _build_ui(self):
        # Header
        self.grid_rowconfigure(6, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Header
        header_frame = ctk.CTkFrame(self)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        header_frame.grid_columnconfigure(2, weight=1)
        back_button = ctk.CTkButton(header_frame, text="← Back", command=self.on_back, width=100)
        back_button.grid(row=0, column=0, sticky="w")
        icon_label = ctk.CTkLabel(header_frame, text="📦", font=ctk.CTkFont(size=32, weight="bold"))
        icon_label.grid(row=0, column=1, padx=10)
        title_label = ctk.CTkLabel(header_frame, text="Archive Converter", font=ctk.CTkFont(size=24, weight="bold"))
        title_label.grid(row=0, column=2, padx=10, sticky="w")

        # File selection
        file_frame = ctk.CTkFrame(self)
        file_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        file_frame.grid_columnconfigure(2, weight=1)
        browse_button = ctk.CTkButton(file_frame, text="Browse Files/Folders", command=self.browse_files)
        browse_button.grid(row=0, column=0, sticky="w")
        clear_button = ctk.CTkButton(file_frame, text="Clear", command=self.clear_selection)
        clear_button.grid(row=0, column=1, padx=10, sticky="w")
        self.file_listbox = ctk.CTkTextbox(file_frame, height=80)
        self.file_listbox.grid(row=0, column=2, sticky="ew", padx=10)

        # Format selection
        format_frame = ctk.CTkFrame(self)
        format_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        format_label = ctk.CTkLabel(format_frame, text="Archive Format:")
        format_label.grid(row=0, column=0, sticky="w")
        self.format_var = ctk.StringVar(value="ZIP")
        format_dropdown = ctk.CTkOptionMenu(format_frame, variable=self.format_var, values=["ZIP", "7Z", "TAR"])
        format_dropdown.grid(row=0, column=1, padx=10, sticky="w")
        format_dropdown.tooltip_text = "Choose archive format"

        # Action selection
        action_frame = ctk.CTkFrame(self)
        action_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=10)
        action_label = ctk.CTkLabel(action_frame, text="Action:")
        action_label.grid(row=0, column=0, sticky="w")
        self.action_var = ctk.StringVar(value="Create Archive")
        action_dropdown = ctk.CTkOptionMenu(action_frame, variable=self.action_var, values=["Create Archive", "Extract Archive", "Convert Archive"])
        action_dropdown.grid(row=0, column=1, padx=10, sticky="w")
        action_dropdown.tooltip_text = "Choose what to do with the archive"

        # Output directory
        output_frame = ctk.CTkFrame(self)
        output_frame.grid(row=4, column=0, sticky="ew", padx=20, pady=10)
        output_button = ctk.CTkButton(output_frame, text="Select Output Folder", command=self.browse_output_dir)
        output_button.grid(row=0, column=0, sticky="w")
        output_button.tooltip_text = "Where converted/extracted files will be saved"
        self.output_label = ctk.CTkLabel(output_frame, text="No directory selected.", text_color="gray")
        self.output_label.grid(row=0, column=1, padx=10, sticky="w")

        # Start button
        action_btn_frame = ctk.CTkFrame(self)
        action_btn_frame.grid(row=5, column=0, sticky="ew", padx=20, pady=10)
        start_button = ctk.CTkButton(action_btn_frame, text="Start", command=self.start_conversion)
        start_button.grid(row=0, column=0, sticky="w")
        start_button.tooltip_text = "Begin conversion or extraction"

        # Progress and status
        progress_frame = ctk.CTkFrame(self)
        progress_frame.grid(row=6, column=0, sticky="ew", padx=20, pady=10)
        progress_frame.grid_columnconfigure(0, weight=1)
        self.progress_bar = ctk.CTkProgressBar(progress_frame)
        self.progress_bar.grid(row=0, column=0, sticky="ew")
        self.progress_bar.set(0)
        self.status_label = ctk.CTkLabel(progress_frame, textvariable=self.status_var, text_color="gray")
        self.status_label.grid(row=0, column=1, padx=10, sticky="w")

    # Event Handlers
    def browse_files(self):
        from tkinter import filedialog
        files = filedialog.askopenfilenames(title="Select Files or Archives")
        if files:
            self.selected_files = list(files)
            self.update_file_list()

    def update_file_list(self):
        self.file_listbox.configure(state="normal")
        self.file_listbox.delete("1.0", "end")
        if not self.selected_files:
            self.file_listbox.insert("end", "No files selected.")
        else:
            for f in self.selected_files:
                self.file_listbox.insert("end", f + "\n")
        self.file_listbox.configure(state="disabled")
    def clear_selection(self):
        self.selected_files = []
        self.update_file_list()
    def format_changed(self):
        self.selected_format = self.format_var.get()
    def action_changed(self):
        self.action_type = self.action_var.get()
    def browse_output_dir(self):
        from tkinter import filedialog
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir = directory
            self.output_label.configure(text=f"Output Path: {self.output_dir}")
    def start_conversion(self):
        import threading
        if not self.selected_files:
            self._show_notification("No files selected.", type_="warning")
            return
        if not self.output_dir:
            self._show_notification("No output directory selected.", type_="warning")
            return
        self.status_var.set("Preparing...")
        self.progress_bar.set(0)
        thread = threading.Thread(target=self._run_conversion_thread)
        thread.daemon = True
        thread.start()
    def open_output_folder(self):
        import os
        import platform
        import subprocess
        if self.output_dir and os.path.isdir(self.output_dir):
            system = platform.system()
            try:
                if system == "Windows":
                    os.startfile(self.output_dir)
                elif system == "Darwin":
                    subprocess.run(["open", self.output_dir], check=True)
                else:
                    subprocess.run(["xdg-open", self.output_dir], check=True)
            except Exception as e:
                self._show_notification(f"Could not open the output folder: {e}", type_="warning")
        else:
            self._show_notification("No valid output directory selected.", type_="warning")

    # Backend Methods
    def _run_conversion_thread(self):
        import time
        import os
        import zipfile
        import tarfile
        try:
            try:
                import py7zr
                has_py7zr = True
            except ImportError:
                has_py7zr = False
            self._update_ui_state(converting=True)
            action = self.action_var.get()
            format_ = self.format_var.get()
            total = len(self.selected_files)
            for idx, file in enumerate(self.selected_files):
                self.status_var.set(f"({idx+1}/{total}) Processing: {os.path.basename(file)}")
                self.progress_bar.set((idx+1)/total)
                time.sleep(0.2)  # Simulate work
                if action == "Create Archive":
                    out_path = os.path.join(self.output_dir, f"archive_{idx+1}.{format_.lower()}")
                    if format_ == "ZIP":
                        with zipfile.ZipFile(out_path, 'w') as zf:
                            zf.write(file, os.path.basename(file))
                    elif format_ == "TAR":
                        with tarfile.open(out_path, 'w') as tf:
                            tf.add(file, arcname=os.path.basename(file))
                    elif format_ == "7Z" and has_py7zr:
                        with py7zr.SevenZipFile(out_path, 'w') as zf:
                            zf.write(file, os.path.basename(file))
                    elif format_ == "7Z":
                        self._show_notification("py7zr not installed. Cannot create 7Z archives.", type_="error")
                elif action == "Extract Archive":
                    if format_ == "ZIP":
                        with zipfile.ZipFile(file, 'r') as zf:
                            zf.extractall(self.output_dir)
                    elif format_ == "TAR":
                        with tarfile.open(file, 'r') as tf:
                            tf.extractall(self.output_dir)
                    elif format_ == "7Z" and has_py7zr:
                        with py7zr.SevenZipFile(file, 'r') as zf:
                            zf.extractall(path=self.output_dir)
                    elif format_ == "7Z":
                        self._show_notification("py7zr not installed. Cannot extract 7Z archives.", type_="error")
                elif action == "Convert Archive":
                    # For simplicity, extract then re-archive in new format
                    temp_dir = os.path.join(self.output_dir, f"temp_extract_{idx+1}")
                    os.makedirs(temp_dir, exist_ok=True)
                    if file.endswith('.zip'):
                        with zipfile.ZipFile(file, 'r') as zf:
                            zf.extractall(temp_dir)
                    elif file.endswith('.tar'):
                        with tarfile.open(file, 'r') as tf:
                            tf.extractall(temp_dir)
                    elif file.endswith('.7z') and has_py7zr:
                        with py7zr.SevenZipFile(file, 'r') as zf:
                            zf.extractall(path=temp_dir)
                    elif file.endswith('.7z'):
                        self._show_notification("py7zr not installed. Cannot convert 7Z archives.", type_="error")
                    out_path = os.path.join(self.output_dir, f"converted_{idx+1}.{format_.lower()}")
                    if format_ == "ZIP":
                        with zipfile.ZipFile(out_path, 'w') as zf:
                            for root, _, files in os.walk(temp_dir):
                                for f in files:
                                    zf.write(os.path.join(root, f), f)
                    elif format_ == "TAR":
                        with tarfile.open(out_path, 'w') as tf:
                            for root, _, files in os.walk(temp_dir):
                                for f in files:
                                    tf.add(os.path.join(root, f), arcname=f)
                    elif format_ == "7Z" and has_py7zr:
                        with py7zr.SevenZipFile(out_path, 'w') as zf:
                            for root, _, files in os.walk(temp_dir):
                                for f in files:
                                    zf.write(os.path.join(root, f), f)
                    elif format_ == "7Z":
                        self._show_notification("py7zr not installed. Cannot create 7Z archives.", type_="error")
                    # Clean up temp_dir
                    import shutil
                    shutil.rmtree(temp_dir)
            self.status_var.set("Done!")
            self.progress_bar.set(1)
            self._show_notification("Conversion finished.", type_="success")
        except Exception as e:
            self._show_notification(f"Error: {e}", type_="error")
        finally:
            self._update_ui_state(converting=False)
    def _update_ui_state(self, converting: bool):
        # Optionally disable/enable buttons during conversion
        state = "disabled" if converting else "normal"
        # ...existing code...
    def _show_notification(self, message, type_="info"):
        # Simple notification: update status label
        self.status_var.set(message)