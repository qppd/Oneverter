import customtkinter as ctk
from .base_converter import BaseConverter
from tkinter import filedialog, Listbox, Scrollbar, SINGLE, MULTIPLE, END, messagebox
import os
from PIL import Image, ImageEnhance
from .base_converter import BaseConverter
import customtkinter as ctk
from rembg import remove

class ImageConverter(BaseConverter):
    def get_supported_formats(self):
        return [".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff"]

    def convert(self, input_path, output_path, options):
        try:
            img = Image.open(input_path)

            if options.get("remove_bg"):
                img = remove(img)

            if options.get("brightness") != 1.0:
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(options["brightness"])
            
            if options.get("contrast") != 1.0:
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(options["contrast"])

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

            save_options = {"format": options["format"]}
            if options["format"].lower() in ["jpeg", "jpg", "webp"]:
                save_options["quality"] = options.get("compression", 95)
            
            img.save(output_path, **save_options)
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
        from ui.theme import get_frame_style, get_button_style, get_label_style
        
        selection_frame = ctk.CTkFrame(self.parent, **get_frame_style("card"))
        selection_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        selection_frame.grid_columnconfigure(1, weight=1)

        # Title
        title_label = ctk.CTkLabel(selection_frame, text="📁 File Selection", **get_label_style("subheading"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(20, 15), padx=20, sticky="w")

        select_button = ctk.CTkButton(selection_frame, text="Select Images", command=self.select_files, **get_button_style("secondary"))
        select_button.grid(row=1, column=0, padx=20, pady=(0, 20))

        self.file_listbox = Listbox(selection_frame, selectmode=MULTIPLE, bg="#2b2b2b", fg="white", borderwidth=0, highlightthickness=0, height=8)
        self.file_listbox.grid(row=1, column=1, padx=(10, 10), pady=(0, 20), sticky="ew")

        scrollbar = Scrollbar(selection_frame, orient="vertical", command=self.file_listbox.yview)
        scrollbar.grid(row=1, column=2, sticky="ns", pady=(0, 20))
        self.file_listbox.config(yscrollcommand=scrollbar.set)

        clear_button = ctk.CTkButton(selection_frame, text="Clear", command=self.clear_files, **get_button_style("danger", "small"))
        clear_button.grid(row=1, column=3, padx=(10, 20), pady=(0, 20))

        options_frame = ctk.CTkFrame(self.parent, **get_frame_style("card"))
        options_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)

        # Title
        options_title = ctk.CTkLabel(options_frame, text="⚙️ Conversion Options", **get_label_style("subheading"))
        options_title.grid(row=0, column=0, columnspan=10, pady=(20, 15), padx=20, sticky="w")

        format_label = ctk.CTkLabel(options_frame, text="Format:", **get_label_style("body"))
        format_label.grid(row=1, column=0, padx=(20, 10), pady=10, sticky="w")
        self.format_var = ctk.StringVar(value="PNG")
        format_menu = ctk.CTkOptionMenu(options_frame, variable=self.format_var, values=["PNG", "JPG", "BMP", "WEBP", "TIFF"], **get_button_style("secondary", "small"))
        format_menu.grid(row=1, column=1, padx=10, pady=10)

        resize_label = ctk.CTkLabel(options_frame, text="Resize (WxH):", **get_label_style("body"))
        resize_label.grid(row=1, column=2, padx=(20, 10), pady=10, sticky="w")
        self.width_var = ctk.StringVar()
        self.height_var = ctk.StringVar()
        width_entry = ctk.CTkEntry(options_frame, textvariable=self.width_var, width=80, placeholder_text="Width")
        width_entry.grid(row=1, column=3, padx=5, pady=10)
        height_entry = ctk.CTkEntry(options_frame, textvariable=self.height_var, width=80, placeholder_text="Height")
        height_entry.grid(row=1, column=4, padx=5, pady=10)

        self.grayscale_var = ctk.BooleanVar()
        grayscale_check = ctk.CTkCheckBox(options_frame, text="Grayscale", variable=self.grayscale_var, **get_label_style("body"))
        grayscale_check.grid(row=1, column=5, padx=20, pady=10, sticky="w")

        self.flip_var = ctk.StringVar(value="None")
        flip_label = ctk.CTkLabel(options_frame, text="Flip:", **get_label_style("body"))
        flip_label.grid(row=1, column=6, padx=(20, 10), pady=10, sticky="w")
        flip_menu = ctk.CTkOptionMenu(options_frame, variable=self.flip_var, values=["None", "Horizontal", "Vertical"], **get_button_style("secondary", "small"))
        flip_menu.grid(row=1, column=7, padx=10, pady=10)

        self.rotate_var = ctk.StringVar(value="0")
        rotate_label = ctk.CTkLabel(options_frame, text="Rotate:", **get_label_style("body"))
        rotate_label.grid(row=1, column=8, padx=(20, 10), pady=10, sticky="w")
        rotate_menu = ctk.CTkOptionMenu(options_frame, variable=self.rotate_var, values=["0", "90", "180", "270"], **get_button_style("secondary", "small"))
        rotate_menu.grid(row=1, column=9, padx=(10, 20), pady=10)

        # Editing options
        edit_frame = ctk.CTkFrame(self.parent, **get_frame_style("card"))
        edit_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)

        # Title
        edit_title = ctk.CTkLabel(edit_frame, text="✨ Enhancements", **get_label_style("subheading"))
        edit_title.grid(row=0, column=0, columnspan=7, pady=(20, 15), padx=20, sticky="w")

        self.remove_bg_var = ctk.BooleanVar()
        remove_bg_check = ctk.CTkCheckBox(edit_frame, text="Remove Background", variable=self.remove_bg_var, **get_label_style("body"))
        remove_bg_check.grid(row=1, column=0, padx=20, pady=10, sticky="w")

        compression_label = ctk.CTkLabel(edit_frame, text="Compression:", **get_label_style("body"))
        compression_label.grid(row=1, column=1, padx=(40, 10), pady=10, sticky="w")
        self.compression_var = ctk.IntVar(value=95)
        compression_slider = ctk.CTkSlider(edit_frame, from_=0, to=100, variable=self.compression_var)
        compression_slider.grid(row=1, column=2, padx=10, pady=10, sticky="ew")

        brightness_label = ctk.CTkLabel(edit_frame, text="Brightness:", **get_label_style("body"))
        brightness_label.grid(row=1, column=3, padx=(40, 10), pady=10, sticky="w")
        self.brightness_var = ctk.DoubleVar(value=1.0)
        brightness_slider = ctk.CTkSlider(edit_frame, from_=0.5, to=1.5, variable=self.brightness_var)
        brightness_slider.grid(row=1, column=4, padx=10, pady=10, sticky="ew")

        contrast_label = ctk.CTkLabel(edit_frame, text="Contrast:", **get_label_style("body"))
        contrast_label.grid(row=1, column=5, padx=(40, 10), pady=10, sticky="w")
        self.contrast_var = ctk.DoubleVar(value=1.0)
        contrast_slider = ctk.CTkSlider(edit_frame, from_=0.5, to=1.5, variable=self.contrast_var)
        contrast_slider.grid(row=1, column=6, padx=10, pady=(10, 20), sticky="ew")

        edit_frame.grid_columnconfigure((2, 4, 6), weight=1)


        output_frame = ctk.CTkFrame(self.parent, **get_frame_style("card"))
        output_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=10)
        output_frame.grid_columnconfigure(1, weight=1)

        # Title
        output_title = ctk.CTkLabel(output_frame, text="📂 Output Settings", **get_label_style("subheading"))
        output_title.grid(row=0, column=0, columnspan=3, pady=(20, 15), padx=20, sticky="w")

        output_button = ctk.CTkButton(output_frame, text="Select Folder", command=self.select_output_folder, **get_button_style("secondary"))
        output_button.grid(row=1, column=0, padx=20, pady=(0, 20))

        self.output_folder_var = ctk.StringVar(value="Same folder")
        output_label = ctk.CTkLabel(output_frame, textvariable=self.output_folder_var, fg_color="#2b2b2b", text_color="white", corner_radius=8, **get_label_style("caption"))
        output_label.grid(row=1, column=1, padx=10, pady=(0, 20), sticky="ew")

        self.same_folder_var = ctk.BooleanVar(value=True)
        same_folder_check = ctk.CTkCheckBox(output_frame, text="Save in same folder", variable=self.same_folder_var, command=self.toggle_output_folder, **get_label_style("body"))
        same_folder_check.grid(row=1, column=2, padx=(10, 20), pady=(0, 20))

        action_frame = ctk.CTkFrame(self.parent, **get_frame_style("card"))
        action_frame.grid(row=4, column=0, sticky="ew", padx=20, pady=(10, 20))
        action_frame.grid_columnconfigure(1, weight=1)

        # Title
        action_title = ctk.CTkLabel(action_frame, text="🚀 Convert", **get_label_style("subheading"))
        action_title.grid(row=0, column=0, columnspan=2, pady=(20, 15), padx=20, sticky="w")

        self.start_button = ctk.CTkButton(action_frame, text="Start Conversion", command=self.start_conversion, **get_button_style("primary", "large"))
        self.start_button.grid(row=1, column=0, padx=20, pady=(0, 20))

        self.progress_bar = ctk.CTkProgressBar(action_frame)
        self.progress_bar.grid(row=1, column=1, padx=(10, 20), pady=(0, 20), sticky="ew")
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
                "rotate": int(self.rotate_var.get()),
                "remove_bg": self.remove_bg_var.get(),
                "compression": self.compression_var.get(),
                "brightness": self.brightness_var.get(),
                "contrast": self.contrast_var.get()
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