import customtkinter as ctk
from tkinter import messagebox
from .theme import Colors, Fonts
import os
import webbrowser

class NotificationManager:
    """Manages notification toasts for the app."""
    def __init__(self, master):
        self.master = master
        self.active_toasts = []

    def show_toast(self, message, type_="info", duration=3000):
        # Stack toasts vertically, animate fade-in, and support keyboard dismissal
        y_offset = 0.05 + 0.08 * len(self.active_toasts)
        toast = ctk.CTkFrame(self.master, fg_color=self._get_color(type_), corner_radius=8)
        label = ctk.CTkLabel(toast, text=message, font=Fonts.BODY, text_color=Colors.BACKGROUND)
        label.pack(padx=16, pady=10)
        toast.place(relx=0.5, rely=y_offset, anchor="n")
        self.active_toasts.append(toast)

        def destroy_toast():
            if toast in self.active_toasts:
                self.active_toasts.remove(toast)
            toast.destroy()
        toast.after(duration, destroy_toast)

        # Accessibility: allow Escape key to dismiss
        toast.bind_all('<Escape>', lambda e: destroy_toast())

        # Animate fade-in (simple opacity effect)
        try:
            for alpha in range(0, 100, 10):
                toast.after(alpha*2, lambda a=alpha: toast.wm_attributes('-alpha', a/100))
        except Exception:
            pass

    def _get_color(self, type_):
        if type_ == "success":
            return Colors.SUCCESS
        if type_ == "error":
            return Colors.ACCENT
        if type_ == "warning":
            return "#d08770"
        return Colors.BUTTON

class ErrorDialog:
    """Reusable error dialog with logging and reporting."""
    @staticmethod
    def show_error(master, title, message, log_path=None):
        import webbrowser
        def view_log():
            if log_path and os.path.exists(log_path):
                with open(log_path, "r") as f:
                    log_content = f.read()
                messagebox.showinfo("Error Log", log_content)
            else:
                messagebox.showinfo("Error Log", "No log file found.")
        dialog = ctk.CTkToplevel(master)
        dialog.title(title)
        dialog.geometry("420x240")
        dialog.resizable(False, False)
        frame = ctk.CTkFrame(dialog, fg_color=Colors.FRAME, corner_radius=10)
        frame.pack(expand=True, fill="both", padx=20, pady=20)
        label = ctk.CTkLabel(frame, text=message, font=Fonts.BODY, text_color=Colors.ACCENT, wraplength=360)
        label.pack(pady=(0, 16))
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(pady=8)
        btn_retry = ctk.CTkButton(btn_frame, text="Retry", command=dialog.destroy, fg_color=Colors.BUTTON)
        btn_retry.pack(side="left", padx=8)
        btn_log = ctk.CTkButton(btn_frame, text="View Log", command=view_log, fg_color=Colors.BUTTON_HOVER)
        btn_log.pack(side="left", padx=8)
        btn_report = ctk.CTkButton(btn_frame, text="Report Issue", command=lambda: ErrorDialog._report_issue(message), fg_color=Colors.ACCENT)
        btn_report.pack(side="left", padx=8)

        # Accessibility: focus first button, allow Escape to close
        btn_retry.focus_set()
        dialog.bind('<Escape>', lambda e: dialog.destroy())

        # Keyboard navigation: Tab between buttons
        for btn in [btn_retry, btn_log, btn_report]:
            btn.bind('<Tab>', lambda e: btn_log.focus_set() if e.widget==btn_retry else btn_report.focus_set() if e.widget==btn_log else btn_retry.focus_set())

    @staticmethod
    def _report_issue(message):
        # Open GitHub issues page or email client
        github_url = "https://github.com/qppd/Oneverter/issues/new"
        try:
            webbrowser.open(github_url)
        except Exception:
            messagebox.showinfo("Report Issue", "Please copy the error and report it on GitHub or contact support.")
