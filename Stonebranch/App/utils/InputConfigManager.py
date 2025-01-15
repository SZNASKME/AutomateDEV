import customtkinter as ctk
import json

from utils.pathHolder import INPUT_CONFIG_JSON_PATH

class UserConfigPopUp(ctk.CTkToplevel):
    def __init__(self, master, button_widget, on_save_callback):
        super().__init__(master)
        self.master = master
        self.button_widget = button_widget
        self.on_save_callback = on_save_callback
        self.field_definitions = InputConfigManager().user_input_config
        self.field_widgets = {}  # Store widgets for later retrieval
        
        # Configure the popup window
        self.overrideredirect(True)  # Removes title bar
        self.geometry(self.calculatePosition())  # Position near the button
        self.bind("<FocusOut>", self.onFocusOut)  # Close when clicking outside

        # Create dynamic fields
        self.createFields()

        # Save button
        save_button = ctk.CTkButton(self, text="Save", command=self.saveAndClose)
        save_button.pack(padx=10, pady=(0, 10))

    def calculatePosition(self):
        """Position the popup near the button."""
        x = self.button_widget.winfo_rootx()
        y = self.button_widget.winfo_rooty() + self.button_widget.winfo_height() + 5
        return f"+{x}+{y}"

    def createFields(self):
        """Dynamically create input fields based on the provided definitions."""
        for field in self.field_definitions:
            field_type = field.get("type", "entry")
            label = field.get("label", "Field")
            options = field.get("options", [])
            default_value = field.get("default", "")

            # Add a label
            ctk.CTkLabel(self, text=label).pack(padx=10, pady=(10, 0))

            # Add the input field
            if field_type == "entry":
                entry = ctk.CTkEntry(self, placeholder_text=default_value)
                entry.pack(padx=10, pady=5)
                self.field_widgets[field["name"]] = entry
            elif field_type == "dropdown":
                dropdown = ctk.CTkOptionMenu(self, values=options)
                dropdown.set(default_value)
                dropdown.pack(padx=10, pady=5)
                self.field_widgets[field["name"]] = dropdown
            elif field_type == "checkbox":
                checkbox_var = ctk.BooleanVar(value=default_value)
                checkbox = ctk.CTkCheckBox(self, text=label, variable=checkbox_var)
                checkbox.pack(padx=10, pady=5)
                self.field_widgets[field["name"]] = checkbox_var  # Save the variable

    def onFocusOut(self, event):
        """Close the popup when focus is lost."""
        self.destroy()

    def saveAndClose(self):
        """Collect values from fields, save them, and close the popup."""
        values = {}
        for field_name, widget in self.field_widgets.items():
            if isinstance(widget, ctk.CTkEntry):
                values[field_name] = widget.get()
            elif isinstance(widget, ctk.CTkOptionMenu):
                values[field_name] = widget.get()
            elif isinstance(widget, ctk.BooleanVar):  # Checkbox
                values[field_name] = widget.get()
        
        if self.on_save_callback:
            self.on_save_callback(values)  # Pass all field values as a dictionary
        self.destroy()

class InputConfigManager:
    def __init__(self):
        self.user_input_config = self.loadConfig()

    ########################################
    # Features
    ########################################
    
    def loadConfig(self):
        #Loads the features from the JSON file.
        try:
            with open(INPUT_CONFIG_JSON_PATH, 'r') as f:
                data = json.load(f)
                return data.get('configs', [])
        except FileNotFoundError:
            print("Features JSON file not found. Creating a default one.")
            # Default features if the file is missing
            return []