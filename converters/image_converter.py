import customtkinter as ctk
from .base_converter import BaseConverter
from tkinter import filedialog, Listbox, Scrollbar, SINGLE, MULTIPLE, END, messagebox
import os
from PIL import Image

class ImageConverter(BaseConverter):
    def get_supported_formats(self):
        return [".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff"]

    def convert(self, input_path, output_path, options):
        try:
            img = Image.open(input_path)

            if options.get("resize"):
                img = img.resize(options["resize"])

            if options.get("grayscale"):
                img = img.convert("L")

            if options.get("flip") == "Horizontal":
                img = img.transpose(Image.FLIP_LEFT_RIGHT)
            elif options.get("flip") == "Vertical":
                img = img.transpose(Image.FLIP_TOP_BOTTOM)

            if options.get("rotate", 0) != 0:
                img = img.rotate(options["rotate"], expand=True)

            img.save(output_path, format=options["format"])
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to convert {input_path}:\n{e}")
            return False

class ImageConverterUI:
    def __init__(self, parent_frame: ctk.CTkFrame):
        self.parent = parent_frame
        self.converter = ImageConverter()
        self.create_widgets()

    def create_widgets(self):
        selection_frame = ctk.CTkFrame(self.parent)
        selection_frame.pack(padx=10, pady=10, fill="x")

        select_button = ctk.CTkButton(selection_frame, text="Select Images", command=self.select_files)
        select_button.pack(side="left", padx=(0, 10))

        self.file_listbox = Listbox(selection_frame, selectmode=MULTIPLE, bg="#2b2b2b", fg="white", borderwidth=0, highlightthickness=0)
        self.file_listbox.pack(side="left", fill="both", expand=True)

        scrollbar = Scrollbar(selection_frame, orient="vertical", command=self.file_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.file_listbox.config(yscrollcommand=scrollbar.set)

        options_frame = ctk.CTkFrame(self.parent)
        options_frame.pack(padx=10, pady=10, fill="x")

        format_label = ctk.CTkLabel(options_frame, text="Convert to:")
        format_label.pack(side="left", padx=(0, 10))
        self.format_var = ctk.StringVar(value="PNG")
        format_menu = ctk.CTkOptionMenu(options_frame, variable=self.format_var, values=["PNG", "JPG", "BMP", "WEBP", "TIFF"])
        format_menu.pack(side="left", padx=(0, 20))

        resize_label = ctk.CTkLabel(options_frame, text="Resize (WxH):")
        resize_label.pack(side="left", padx=(0, 10))
        self.width_var = ctk.StringVar()
        self.height_var = ctk.StringVar()
        width_entry = ctk.CTkEntry(options_frame, textvariable=self.width_var, width=60)
        width_entry.pack(side="left")
        height_entry = ctk.CTkEntry(options_frame, textvariable=self.height_var, width=60)
        height_entry.pack(side="left", padx=(5, 20))

        self.grayscale_var = ctk.BooleanVar()
        grayscale_check = ctk.CTkCheckBox(options_frame, text="Grayscale", variable=self.grayscale_var)
        grayscale_check.pack(side="left")

        self.flip_var = ctk.StringVar(value="None")
        flip_label = ctk.CTkLabel(options_frame, text="Flip:")
        flip_label.pack(side="left", padx=(20, 10))
        flip_menu = ctk.CTkOptionMenu(options_frame, variable=self.flip_var, values=["None", "Horizontal", "Vertical"])
        flip_menu.pack(side="left")

        self.rotate_var = ctk.StringVar(value="0")
        rotate_label = ctk.CTkLabel(options_frame, text="Rotate:")
        rotate_label.pack(side="left", padx=(20, 10))
        rotate_menu = ctk.CTkOptionMenu(options_frame, variable=self.rotate_var, values=["0", "90", "180", "270"])
        rotate_menu.pack(side="left")

        output_frame = ctk.CTkFrame(self.parent)
        output_frame.pack(padx=10, pady=10, fill="x")

        output_button = ctk.CTkButton(output_frame, text="Output Folder", command=self.select_output_folder)
        output_button.pack(side="left", padx=(0, 10))

        self.output_folder_var = ctk.StringVar(value="Same folder")
        output_label = ctk.CTkLabel(output_frame, textvariable=self.output_folder_var, fg_color="#2b2b2b", text_color="white", corner_radius=5)
        output_label.pack(side="left", fill="x", expand=True)

        self.same_folder_var = ctk.BooleanVar(value=True)
        same_folder_check = ctk.CTkCheckBox(output_frame, text="Save in same folder", variable=self.same_folder_var, command=self.toggle_output_folder)
        same_folder_check.pack(side="left", padx=(10, 0))

        action_frame = ctk.CTkFrame(self.parent)
        action_frame.pack(padx=10, pady=10, fill="x")

        self.start_button = ctk.CTkButton(action_frame, text="Start Conversion", command=self.start_conversion)
        self.start_button.pack(side="left", padx=(0, 10))

        self.progress_bar = ctk.CTkProgressBar(action_frame)
        self.progress_bar.pack(side="left", fill="x", expand=True)
        self.progress_bar.set(0)

    def start_conversion(self):
        files_to_convert = self.file_listbox.get(0, END)
        if not files_to_convert:
            messagebox.showerror("Error", "No files selected for conversion.")
            return

        output_folder = self.output_folder_var.get()
        if not self.same_folder_var.get() and not os.path.isdir(output_folder):
            messagebox.showerror("Error", "Output folder not found.")
            return

        total_files = len(files_to_convert)
        for i, filepath in enumerate(files_to_convert):
            original_dir = os.path.dirname(filepath)
            filename = os.path.basename(filepath)
            name, _ = os.path.splitext(filename)
            output_format = self.format_var.get().lower()

            save_dir = output_folder if not self.same_folder_var.get() else original_dir
            new_filepath = os.path.join(save_dir, f"{name}.{output_format}")

            options = {
                "format": self.format_var.get(),
                "resize": (int(self.width_var.get()), int(self.height_var.get())) if self.width_var.get() and self.height_var.get() else None,
                "grayscale": self.grayscale_var.get(),
                "flip": self.flip_var.get(),
                "rotate": int(self.rotate_var.get())
            }

            if self.converter.convert(filepath, new_filepath, options):
                progress = (i + 1) / total_files
                self.progress_bar.set(progress)
                self.parent.update_idletasks()

        messagebox.showinfo("Success", "All files converted successfully!")
        self.progress_bar.set(0)

    def select_output_folder(self):
        folder_path = filedialog.askdirectory(title="Select Output Folder")
        if folder_path:
            self.output_folder_var.set(folder_path)
            self.same_folder_var.set(False)

    def toggle_output_folder(self):
        if self.same_folder_var.get():
            self.output_folder_var.set("Same folder")
        else:
            self.output_folder_var.set("")

    def select_files(self):
        filepaths = filedialog.askopenfilenames(
            title="Select Images",
            filetypes=(
                ("Image files", "*.jpg *.jpeg *.png *.bmp *.webp *.tiff"),
                ("All files", "*.*")
            )
        )
        if filepaths:
            self.file_listbox.delete(0, END)
            for f in filepaths:
                self.file_listbox.insert(END, f)