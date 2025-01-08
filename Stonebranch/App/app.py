import sys
import os
import customtkinter as ctk
import tkinter as tk
import logging
import pandas as pd

from tkinter.scrolledtext import ScrolledText
from tkinter import filedialog
from utils.pathHolder import APP_LOGO_PATH
from utils.featuresManager import FeatureManager
from utils.globalVariable import GlobalVariable

# Sets the appearance of the window
ctk.set_appearance_mode("light")
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
        self.grid_columnconfigure(0, weight=1, minsize=1000)  # Main UI area
        self.grid_columnconfigure(1, weight=1)  # Sidebar (hidden by default)
        self.grid_rowconfigure(0, weight=1)

        self.featureManager = FeatureManager()
        self.globalVariable = GlobalVariable()
        self.select_feature = tk.StringVar(value="Select Feature")
        self.input_widgets = []
        self.sidebar_visible = True  # Toggle state for the log console

        self.setupUI()
        self.setupConsole()
        self.dynamicInputs()
        self.setupLogging()

    def appIcon(self, path):
        self.iconbitmap(path)


    def setupUI(self):
        # Main Form Area
        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Menu for feature selection using Tkinter Menu
        self.menu_button = ctk.CTkButton(self.form_frame, text="Select Feature", command=self.showCategoriesMenu)
        self.menu_button.grid(row=0, column=0, padx=20, pady=20, sticky="ew")

        # Label to show selected feature
        self.selected_item = ctk.StringVar(value="No Feature Selected")
        self.selection_label = ctk.CTkLabel(self.form_frame, textvariable=self.selected_item)
        self.selection_label.grid(row=0, column=1, padx=20, pady=20, sticky="ew")

        # Execute Button
        self.executeButton = ctk.CTkButton(self.form_frame, text="Execute", command=self.executeSelectedFeature)
        self.executeButton.grid(row=0, column=5, padx=20, pady=20, sticky="ew")

        self.save_button = ctk.CTkButton(self.form_frame, text="Save", command=self.saveSelectedFeatureSettings)
        self.save_button.grid(row=0, column=6, padx=20, pady=20, sticky="ew")

        # Toggle Console Button
        self.toggle_button = ctk.CTkButton(self.form_frame, text="Hide Log Console", command=self.toggle_sidebar)
        self.toggle_button.grid(row=0, column=7, columnspan=1, sticky="ew", padx=10, pady=10)

    def showCategoriesMenu(self):
        self.categories_menu = tk.Menu(self, tearoff=0)
        self.populateCategoriesMenu()
        self.categories_menu.post(self.menu_button.winfo_rootx(), self.menu_button.winfo_rooty() + self.menu_button.winfo_height())

    def toggle_sidebar(self):
        #Toggle the visibility of the sidebar.
        if self.sidebar_visible:
            self.log_frame.grid_remove()  # Hide the sidebar
            self.grid_columnconfigure(1, weight=0)  # Disable sidebar column
            self.toggle_button.configure(text="Show Log Console")
        else:
            self.log_frame.grid()  # Show the sidebar
            self.grid_columnconfigure(1, weight=1)  # Enable sidebar column
            self.toggle_button.configure(text="Hide Log Console")
        self.sidebar_visible = not self.sidebar_visibl


    def transferWidgetValues(self):
        tranfered_values = {}
        all_inputs = self.globalVariable.getAllWidget()
        for key, widget in all_inputs.items():
            if isinstance(widget, ctk.CTkEntry):
                value = widget.get()
            elif isinstance(widget, tk.BooleanVar):
                value = widget.get()
            elif isinstance(widget, ctk.CTkOptionMenu):
                value = widget.get()
            elif isinstance(widget, ctk.CTkLabel):
                value = widget.cget("text")
            else:
                value = None
            tranfered_values[key] = value
        return tranfered_values
    

    def executeSelectedFeature(self):
        self.logger.info("Executing the selected feature...")
        
    def saveSelectedFeatureSettings(self):
        self.logger.info("Saving the selected feature settings...")
        all_inputs = self.transferWidgetValues()
        
    def populateCategoriesMenu(self):
        categories = list({item["category"] for item in self.featureManager.listEnabledFeatures()})
        categories.sort()
        for category in categories:
            category_menu = tk.Menu(self.categories_menu, tearoff=0)
            self.populateNamesMenu(category, category_menu)
            self.categories_menu.add_cascade(label=category, menu=category_menu)

    def populateNamesMenu(self, category, category_menu):
        names = [item["name"] for item in self.featureManager.listEnabledFeatures() if item["category"] == category]
        names.sort()
        for name in names:
            category_menu.add_command(
                label=name, command=lambda n=name: self.selectItem(n)
            )

    def selectItem(self, name):
        self.selected_item.set(f"{name}")
        self.updateInputs(name)  # Update inputs based on the selected feature


    # Sidebar Log Console
    def setupConsole(self):
        self.log_frame = ctk.CTkFrame(self)
        self.log_frame.grid(row=0, column=1, sticky="nse", pady=10)
        self.log_frame.grid_rowconfigure(1, weight=1)

        self.log_console = ScrolledText(self.log_frame, state="disabled", wrap="word")
        self.log_console.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def dynamicInputs(self):
        self.input_frame = ctk.CTkFrame(self.form_frame)
        self.input_frame.grid(row=1, column=0, columnspan=10, padx=20, pady=20, sticky="nsew")


    def updateInputs(self, feature_name):
        # Clear previous input widgets
        for widget in self.input_widgets:
            widget.destroy()
        self.input_widgets.clear()

        # Fetch inputs for the selected feature
        inputs = self.featureManager.getFeatureInputs(feature_name)
        self.queryInputsOutputs(inputs, self.input_frame, self.input_widgets)
        
    
    def queryInputsOutputs(self, IO, frame, widgets: list):
        index = 0
        # Dynamically create input fields
        for IO_field in IO:
            label = ctk.CTkLabel(frame, text=IO_field["label"])
            label.grid(row=index, column=0, padx=20, pady=10, sticky="w")
            widgets.append(label)

            if IO_field["type"] == "text":
                if IO_field.get("hidden", False):
                    # Create password entry
                    password_entry = ctk.CTkEntry(frame, show="*", placeholder_text = IO_field["placeholder"], width=150)
                    password_entry.grid(row=index, column=1, padx=20, pady=10, sticky="ew")
                    widgets.append(password_entry)
                    self.globalVariable.saveWidget(IO_field["name"], password_entry)
                    # Create toggle button
                    def toggle_password(entry=password_entry):
                        if entry.cget("show") == "*":
                            entry.configure(show="")  # Show password
                            toggle_button.configure(text="Hide")
                        else:
                            entry.configure(show="*")  # Hide password
                            toggle_button.configure(text="Show")

                    toggle_button = ctk.CTkButton(
                        frame, text="Show", command=toggle_password
                    )
                    toggle_button.grid(row=index, column=2, padx=10, pady=10, sticky="w")
                    widgets.append(toggle_button)
                else:
                    entry = ctk.CTkEntry(frame, placeholder_text=IO_field["placeholder"], width=150)
                    entry.grid(row=index, column=1, padx=20, pady=10, sticky="ew")
                    widgets.append(entry)
                    self.globalVariable.saveWidget(IO_field["name"], entry)

            elif IO_field["type"] == "checkbox":
                var = tk.BooleanVar()
                checkbox = ctk.CTkCheckBox(frame, text=IO_field["label"], variable=var)
                checkbox.grid(row=index, column=1, padx=20, pady=10, sticky="w")
                widgets.append(checkbox)
                self.globalVariable.saveWidget(IO_field["name"], var)

            elif IO_field["type"] == "dropdown":
                dropdown = ctk.CTkOptionMenu(frame, values=IO_field["options"], anchor="w")
                dropdown.grid(row=index, column=1, padx=20, pady=10, sticky="ew")
                widgets.append(dropdown)
                self.globalVariable.saveWidget(IO_field["name"], dropdown)

            elif IO_field["type"] == "file":
                file_label = ctk.CTkLabel(frame, text="No file selected")
                browse_button = ctk.CTkButton(
                    frame, text="Browse", 
                    command=lambda lbl=file_label: self.browseFile(lbl, frame, browse_button.grid_info()["row"] - 1),
                    width=30
                )
                browse_button.grid(row=index, column=1, padx=20, pady=10, sticky="w")
                file_label.grid(row=index, column=2, columnspan=2, padx=20, pady=10, sticky="w")
                widgets.append(browse_button)
                widgets.append(file_label)
                self.globalVariable.saveWidget(IO_field["name"], file_label)
            elif IO_field["type"] == "folder":
                folder_label = ctk.CTkLabel(frame, text="No folder selected")
                browse_button = ctk.CTkButton(
                    frame, text="Browse", 
                    command=lambda lbl=folder_label: self.browseFolder(lbl),
                    width=30
                )
                browse_button.grid(row=index, column=1, padx=20, pady=10, sticky="w")
                folder_label.grid(row=index, column=2, columnspan=2, padx=20, pady=10, sticky="w")
                widgets.append(browse_button)
                widgets.append(folder_label)    
            
            index += 1
        frame.grid_columnconfigure(1, weight=1)  # Make column 1 expandable

    def browseFile(self, file_label, frame, index):
        #Browse for a file and update the file label.
        file_path = filedialog.askopenfilename(
            title="Select a file",
            filetypes=[("All files", "*.*"), ("Text files", "*.txt"), ("Excel files", "*.xlsx"), ("JSON files", "*.json")],
        )
        if file_path:
            file_name = os.path.basename(file_path)
            file_label.configure(text=file_name)
            file_type = file_name.split(".")[-1]
            
        if file_type in ["xlsx", "xls"]:  # Only for Excel files
            self.addSheetSelection(file_path, frame, index)  # Dynamically add sheet selection dropdown
        else:
            # Clear sheet selection if it's not an Excel file
            if hasattr(self, 'sheet_dropdown'):
                self.sheet_dropdown.grid_forget()  # Hide the dropdown if it's not an Excel file
                del self.sheet_dropdown  # Remove the attribute to prevent future errors

    def addSheetSelection(self, file_path, frame, index):
        # Load Excel file to get the sheet names
        excel_file = pd.ExcelFile(file_path)
        sheet_names = excel_file.sheet_names

        # If sheet dropdown already exists, destroy it first to prevent multiple dropdowns
        if hasattr(self, 'sheet_dropdown'):
            self.sheet_dropdown.destroy()

        self.sheet_dropdown = ctk.CTkOptionMenu(frame, values=sheet_names, anchor="w")
        self.sheet_dropdown.grid(row=index, column=4, padx=20, pady=10, sticky="ew")
        self.input_widgets.append(self.sheet_dropdown)
        self.globalVariable.saveWidget("sheet_name", self.sheet_dropdown)
        
                
    def browseFolder(self, folder_label):
        #Browse for a folder and update the folder label.
        folder_path = filedialog.askdirectory(title="Select a folder")
        if folder_path:
            folder_label.configure(text=folder_path)


    def setupLogging(self):
        #Set up the logger to write to the log console.
        handler = TextHandler(self.log_console)
        logging.basicConfig(level=logging.INFO, handlers=[handler])
        self.logger = logging.getLogger()


if __name__ == "__main__":
    app = App()
    app.mainloop()
