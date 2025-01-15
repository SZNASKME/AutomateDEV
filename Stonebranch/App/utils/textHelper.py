import customtkinter as ctk
import tkinter as tk
import tkinter.font as font
import logging


class TextHandler(logging.Handler):
    """Custom logging handler to redirect logs to a tkinter Text widget."""
    def __init__(self, widget):
        super().__init__()
        self.widget = widget

    def emit(self, record):
        log_entry = self.format(record)
        self.widget.configure(state="normal")
        self.widget.insert(tk.END, log_entry + "\n")
        self.widget.configure(state="disabled")
        self.widget.yview(tk.END)  # Auto-scroll to the latest log
        
        
class TruncatedLabel(ctk.CTkLabel):
    def __init__(self, master, text_var, max_width, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.max_width = max_width
        self.text_var = text_var
        self.display_text = self.truncate_text(self.text_var.get())
        self.configure(text=self.display_text)

        # Bind the StringVar to dynamically update the label when the value changes
        self.text_var.trace("w", self.update_text)

    def truncate_text(self, text):
        """Truncate text dynamically with ellipses if it exceeds max_width."""
        tk_font = font.Font(family="Arial", size=12)  # Customize the font to match your label
        text_width = tk_font.measure(text)

        if text_width <= self.max_width:
            return text

        for i in range(len(text)):
            truncated_text = text[:i] + "..."
            if tk_font.measure(truncated_text) > self.max_width:
                return text[:i - 1] + "..."
        return text

    def update_text(self, *args):
        """Update the label text and truncate if necessary."""
        self.display_text = self.truncate_text(self.text_var.get())
        self.configure(text=self.display_text)