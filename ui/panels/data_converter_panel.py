import customtkinter as ctk
from converters.data_converter import DataConverterUI
from ..base_converter_panel import BaseConverterPanel


class DataConverterPanel(BaseConverterPanel):
    def on_back(self):
        self.destroy()
    """Panel for the Data Converter, for embedding in unified interface."""
    
    def get_title(self) -> str:
        """Get the panel title."""
        return "📊 Data Converter"
    
    def setup_converter(self):
        """Setup the specific converter UI."""
        self.data_ui = DataConverterUI(self.content_frame)

    def __init__(self, parent):
        super().__init__(parent)
        self._init_state()
        self._build_ui()

    def _init_state(self):
        self.selected_files = []
        self.target_format = None
        self.cleaning_options = {}
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
        icon_label = ctk.CTkLabel(header_frame, text="📊", font=ctk.CTkFont(size=32, weight="bold"))
        icon_label.grid(row=0, column=1, padx=10)
        title_label = ctk.CTkLabel(header_frame, text="Data Converter", font=ctk.CTkFont(size=24, weight="bold"))
        title_label.grid(row=0, column=2, padx=10, sticky="w")

        # File selection
        file_frame = ctk.CTkFrame(self)
        file_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        file_frame.grid_columnconfigure(2, weight=1)
        browse_button = ctk.CTkButton(file_frame, text="Browse Files", command=self.browse_files)
        browse_button.grid(row=0, column=0, sticky="w")
        clear_button = ctk.CTkButton(file_frame, text="Clear", command=self.clear_selection)
        clear_button.grid(row=0, column=1, padx=10, sticky="w")
        self.file_listbox = ctk.CTkTextbox(file_frame, height=80)
        self.file_listbox.grid(row=0, column=2, sticky="ew", padx=10)

        # Format selection
        format_frame = ctk.CTkFrame(self)
        format_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        format_label = ctk.CTkLabel(format_frame, text="Target Format:")
        format_label.grid(row=0, column=0, sticky="w")
        self.format_var = ctk.StringVar(value="CSV")
        format_dropdown = ctk.CTkOptionMenu(format_frame, variable=self.format_var, values=["CSV", "JSON", "XML", "Excel"])
        format_dropdown.grid(row=0, column=1, padx=10, sticky="w")

        # Data options
        options_frame = ctk.CTkFrame(self)
        options_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=10)
        clean_label = ctk.CTkLabel(options_frame, text="Options:")
        clean_label.grid(row=0, column=0, sticky="w")
        self.remove_duplicates_var = ctk.BooleanVar()
        remove_duplicates_cb = ctk.CTkCheckBox(options_frame, text="Remove Duplicates", variable=self.remove_duplicates_var)
        remove_duplicates_cb.grid(row=0, column=1, padx=10, sticky="w")
        self.validate_schema_var = ctk.BooleanVar()
        validate_schema_cb = ctk.CTkCheckBox(options_frame, text="Validate Schema", variable=self.validate_schema_var)
        validate_schema_cb.grid(row=0, column=2, padx=10, sticky="w")

        # Output directory
        output_frame = ctk.CTkFrame(self)
        output_frame.grid(row=4, column=0, sticky="ew", padx=20, pady=10)
        output_button = ctk.CTkButton(output_frame, text="Select Output Folder", command=self.browse_output_dir)
        output_button.grid(row=0, column=0, sticky="w")
        self.output_label = ctk.CTkLabel(output_frame, text="No directory selected.", text_color="gray")
        self.output_label.grid(row=0, column=1, padx=10, sticky="w")

        # Start button
        action_btn_frame = ctk.CTkFrame(self)
        action_btn_frame.grid(row=5, column=0, sticky="ew", padx=20, pady=10)
        start_button = ctk.CTkButton(action_btn_frame, text="Start Conversion", command=self.start_conversion)
        start_button.grid(row=0, column=0, sticky="w")

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
        files = filedialog.askopenfilenames(title="Select Data Files")
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
        self.target_format = self.format_var.get()
    def cleaning_option_changed(self):
        self.cleaning_options['remove_duplicates'] = self.remove_duplicates_var.get()
        self.cleaning_options['validate_schema'] = self.validate_schema_var.get()
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
        import pandas as pd
        try:
            self._update_ui_state(converting=True)
            target_format = self.format_var.get()
            total = len(self.selected_files)
            for idx, file in enumerate(self.selected_files):
                self.status_var.set(f"({idx+1}/{total}) Processing: {os.path.basename(file)}")
                self.progress_bar.set((idx+1)/total)
                time.sleep(0.2)  # Simulate work
                df = None
                # Read file
                if file.endswith('.csv'):
                    df = pd.read_csv(file)
                elif file.endswith('.xlsx') or file.endswith('.xls'):
                    df = pd.read_excel(file)
                elif file.endswith('.json'):
                    df = pd.read_json(file)
                # Add XML support if needed
                # Data cleaning
                if self.cleaning_options.get('remove_duplicates') and df is not None:
                    df = df.drop_duplicates()
                # Save to target format
                out_path = os.path.join(self.output_dir, f"converted_{idx+1}.{target_format.lower()}")
                if target_format == "CSV" and df is not None:
                    df.to_csv(out_path, index=False)
                elif target_format == "Excel" and df is not None:
                    df.to_excel(out_path, index=False)
                elif target_format == "JSON" and df is not None:
                    df.to_json(out_path, orient="records")
                # Add XML export if needed
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