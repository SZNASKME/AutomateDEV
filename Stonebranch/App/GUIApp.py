import sys
import customtkinter as ctk
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import logging
from utils.pathHolder import APP_LOGO_PATH
from utils.featuresManager import FeatureManager

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


class App(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("Stonebranch Toolkit Extended")
        self.appIcon(APP_LOGO_PATH)
        self.geometry(f"{appWidth}x{appHeight}")
        self.grid_columnconfigure((0,1), weight=1)  # Form area   
        #self.grid_columnconfigure(1, weight=1)  # Sidebar (hidden by default)
        self.grid_rowconfigure(0, weight=1)
        self.featureManager = FeatureManager()
        self.select_feature = tk.StringVar(value="Select Feature")
        self.input_widgets = []
        self.sidebar_visible = True  # Toggle state for the log console

        self.setupUI()
        self.setupConsole()
        self.dynamicInputs()
        self.setup_logging()

    def appIcon(self, path):
        self.iconbitmap(path)

    def setupUI(self):
        # Main Form Area
        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        self.featureLabel = ctk.CTkLabel(self.form_frame, text="Features")
        self.featureLabel.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        feature_names = [feature["name"] for feature in self.featureManager.listEnabledFeatures()]
        self.featureDropDown = ctk.CTkOptionMenu(self.form_frame, values=feature_names, variable=self.select_feature, command=self.updateInputs)
        self.featureDropDown.grid(row=0, column=1, padx=20, pady=20, columnspan=4, sticky="ew")

        self.executeButton = ctk.CTkButton(self.form_frame, text="Execute", command=self.generateResults)
        self.executeButton.grid(row=0, column=5, padx=20, pady=20, sticky="ew")

        # Toggle Button
        self.toggle_button = ctk.CTkButton(self.form_frame, text="Hide Log Console", command=self.toggle_sidebar)
        self.toggle_button.grid(row=0, column=6, columnspan=1, sticky="ew", padx=10, pady=10)


    def dynamicInputs(self):
        self.input_frame = ctk.CTkFrame(self.form_frame)
        self.input_frame.grid(row=1, column=0, columnspan=10, padx=20, pady=20, sticky="nsew")

    def setupConsole(self):

        # Sidebar Log Console
        self.log_frame = ctk.CTkFrame(self)
        self.log_frame.grid(row=0, column=1, sticky="nsew")
        self.log_frame.grid_rowconfigure(1, weight=1)

        self.log_console = ScrolledText(self.log_frame, state="disabled", wrap="word")
        self.log_console.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def updateInputs(self, feature_name):
        """Update input fields based on the selected feature."""
        # Clear previous input widgets
        for widget in self.input_widgets:
            widget.destroy()
        self.input_widgets.clear()

        # Fetch inputs for the selected feature
        inputs = self.featureManager.getFeatureInputs(feature_name)

        # Dynamically create input fields
        for input_field in inputs:
            label = ctk.CTkLabel(self.input_frame, text=input_field["label"])
            label.pack(padx=10, pady=5)
            self.input_widgets.append(label)

            if input_field["type"] == "text":
                entry = ctk.CTkEntry(self.input_frame, placeholder_text=input_field["placeholder"])
                entry.pack(padx=10, pady=5)
                self.input_widgets.append(entry)

            elif input_field["type"] == "checkbox":
                var = tk.BooleanVar()
                checkbox = ctk.CTkCheckBox(self.input_frame, text=input_field["label"], variable=var)
                checkbox.pack(padx=10, pady=5)
                self.input_widgets.append(checkbox)

            elif input_field["type"] == "dropdown":
                dropdown = ctk.CTkOptionMenu(self.input_frame, values=input_field["options"])
                dropdown.pack(padx=10, pady=5)
                self.input_widgets.append(dropdown)

    def handle_submit(self):
        """Handle the form submission."""
        # For demonstration purposes, print the inputs
        print("Form submitted!")
        for widget in self.input_widgets:
            if isinstance(widget, ctk.CTkEntry):
                print(f"Text Input: {widget.get()}")
            elif isinstance(widget, ctk.CTkCheckBox):
                print(f"Checkbox: {widget.cget('text')} - {widget.getvar(widget.cget('variable'))}")
            elif isinstance(widget, ctk.CTkOptionMenu):
                print(f"Dropdown: {widget.get()}")
        
    def setup_logging(self):
        """Set up the logger to write to the log console."""
        handler = TextHandler(self.log_console)
        logging.basicConfig(level=logging.INFO, handlers=[handler])
        self.logger = logging.getLogger()

    def toggle_sidebar(self):
        """Toggle the visibility of the sidebar."""
        if self.sidebar_visible:
            self.log_frame.grid_remove()  # Hide the sidebar
            self.grid_columnconfigure(1, weight=0)  # Disable sidebar column
            self.toggle_button.configure(text="Show Log Console")
        else:
            self.log_frame.grid()  # Show the sidebar
            self.grid_columnconfigure(1, weight=1)  # Enable sidebar column
            self.toggle_button.configure(text="Hide Log Console")
        self.sidebar_visible = not self.sidebar_visible

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
