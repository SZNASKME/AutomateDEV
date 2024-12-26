import sys
import os
import customtkinter as ctk
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import logging
from utils.pathHolder import APP_LOGO_PATH

# Sets the appearance of the window
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# Dimensions of the window
appWidth, appHeight = 1600, 900


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


# App Class
class App(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("Stonebranch Toolkit Extended")
        self.appIcon(APP_LOGO_PATH)
        self.geometry(f"{appWidth}x{appHeight}")
        self.grid_columnconfigure(0, weight=3)  # Main UI area
        self.grid_columnconfigure(1, weight=1)  # Log console area
        self.grid_rowconfigure(0, weight=1)

        self.SetupUI()
        self.setup_logging()

    def appIcon(self, path):
        self.iconbitmap(path)

    def SetupUI(self):
        # Main Form Area
        form_frame = ctk.CTkFrame(self)
        form_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.nameLabel = ctk.CTkLabel(form_frame, text="Name")
        self.nameLabel.grid(row=0, column=0, padx=20, pady=20, sticky="ew")

        self.nameEntry = ctk.CTkEntry(form_frame, placeholder_text="Teja")
        self.nameEntry.grid(row=0, column=1, columnspan=3, padx=20, pady=20, sticky="ew")

        self.ageLabel = ctk.CTkLabel(form_frame, text="Age")
        self.ageLabel.grid(row=1, column=0, padx=20, pady=20, sticky="ew")

        self.ageEntry = ctk.CTkEntry(form_frame, placeholder_text="18")
        self.ageEntry.grid(row=1, column=1, columnspan=3, padx=20, pady=20, sticky="ew")

        self.genderLabel = ctk.CTkLabel(form_frame, text="Gender")
        self.genderLabel.grid(row=2, column=0, padx=20, pady=20, sticky="ew")

        self.genderVar = tk.StringVar(value="Prefer not to say")
        self.maleRadioButton = ctk.CTkRadioButton(form_frame, text="Male", variable=self.genderVar, value="He is")
        self.maleRadioButton.grid(row=2, column=1, padx=20, pady=20, sticky="ew")

        self.femaleRadioButton = ctk.CTkRadioButton(form_frame, text="Female", variable=self.genderVar, value="She is")
        self.femaleRadioButton.grid(row=2, column=2, padx=20, pady=20, sticky="ew")

        self.noneRadioButton = ctk.CTkRadioButton(
            form_frame, text="Prefer not to say", variable=self.genderVar, value="They are"
        )
        self.noneRadioButton.grid(row=2, column=3, padx=20, pady=20, sticky="ew")

        self.choiceLabel = ctk.CTkLabel(form_frame, text="Choice")
        self.choiceLabel.grid(row=3, column=0, padx=20, pady=20, sticky="ew")

        self.checkboxVar = tk.StringVar(value="Choice 1")
        self.choice1 = ctk.CTkCheckBox(form_frame, text="choice 1", variable=self.checkboxVar, onvalue="choice1", offvalue="c1")
        self.choice1.grid(row=3, column=1, padx=20, pady=20, sticky="ew")

        self.choice2 = ctk.CTkCheckBox(form_frame, text="choice 2", variable=self.checkboxVar, onvalue="choice2", offvalue="c2")
        self.choice2.grid(row=3, column=2, padx=20, pady=20, sticky="ew")

        self.occupationLabel = ctk.CTkLabel(form_frame, text="Occupation")
        self.occupationLabel.grid(row=4, column=0, padx=20, pady=20, sticky="ew")

        self.occupationOptionMenu = ctk.CTkOptionMenu(form_frame, values=["Student", "Working Professional"])
        self.occupationOptionMenu.grid(row=4, column=1, padx=20, pady=20, columnspan=2, sticky="ew")

        self.generateResultsButton = ctk.CTkButton(
            form_frame, text="Generate Results", command=self.generateResults
        )
        self.generateResultsButton.grid(row=5, column=1, columnspan=2, padx=20, pady=20, sticky="ew")

        #self.displayBox = ctk.CTkTextbox(form_frame, width=200, height=100)
        #self.displayBox.grid(row=6, column=0, columnspan=4, padx=20, pady=20, sticky="nsew")

        form_frame.grid_rowconfigure(6, weight=1)  # Allow the text box to expand

        # Log Console Area
        log_frame = ctk.CTkFrame(self)
        log_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        log_frame.grid_rowconfigure(0, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)

        log_label = ctk.CTkLabel(log_frame, text="Log Console", font=("Arial", 14))
        log_label.grid(row=0, column=0, padx=5, pady=5, sticky="n")

        self.log_console = ScrolledText(log_frame, state="disabled", height=25, width=40, wrap="word")
        self.log_console.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

    def setup_logging(self):
        """Set up the logger to write to the log console."""
        handler = TextHandler(self.log_console)
        logging.basicConfig(level=logging.INFO, handlers=[handler])
        self.logger = logging.getLogger()

    def generateResults(self):
        self.logger.info("Generate Results button clicked.")
        self.displayBox.delete("0.0", "200.0")
        text = self.createText()
        self.displayBox.insert("0.0", text)

    def createText(self):
        checkboxValue = ""
        if self.choice1._check_state and self.choice2._check_state:
            checkboxValue += self.choice1.get() + " and " + self.choice2.get()
        elif self.choice1._check_state:
            checkboxValue += self.choice1.get()
        elif self.choice2._check_state:
            checkboxValue += self.choice2.get()
        else:
            checkboxValue = "none of the available options"

        text = f"{self.nameEntry.get()} : \n{self.genderVar.get()} {self.ageEntry.get()} years old and prefers {checkboxValue}\n"
        text += f"{self.genderVar.get()} currently a {self.occupationOptionMenu.get()}"

        self.logger.info("Generated text: %s", text)
        return text


if __name__ == "__main__":
    app = App()
    app.mainloop()
