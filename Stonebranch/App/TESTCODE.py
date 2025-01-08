import tkinter as tk
import customtkinter as ctk

class NestedDropdownMenuApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Nested Dropdown Menu Example")
        self.geometry("600x400")

        # Sample JSON structure for categories and items
        self.data = [
            {"category": "Fruits", "name": "Apple"},
            {"category": "Fruits", "name": "Banana"},
            {"category": "Vegetables", "name": "Carrot"},
            {"category": "Vegetables", "name": "Broccoli"},
            {"category": "Dairy", "name": "Milk"},
            {"category": "Dairy", "name": "Cheese"},
        ]

        # Menu Bar
        self.menu_bar = tk.Menu(self)

        # Create the root menu
        self.categories_menu = tk.Menu(self.menu_bar, tearoff=0)

        # Add categories to the menu
        self.populate_categories_menu()

        # Add categories menu to the menu bar
        self.menu_bar.add_cascade(label="Features", menu=self.categories_menu)

        # Configure the window to use the menu bar
        self.config(menu=self.menu_bar)

        # Label to show the selected item
        self.selected_item = ctk.StringVar(value="No Selection")
        self.selection_label = ctk.CTkLabel(self, textvariable=self.selected_item)
        self.selection_label.pack(pady=20)

    def populate_categories_menu(self):
        """Populate the categories menu from the JSON data."""
        categories = list({item["category"] for item in self.data})

        for category in categories:
            # Add a cascade menu for each category
            category_menu = tk.Menu(self.categories_menu, tearoff=0)

            # Add items under the category
            self.populate_names_menu(category, category_menu)

            # Add the category to the root menu
            self.categories_menu.add_cascade(label=category, menu=category_menu)

    def populate_names_menu(self, category, category_menu):
        """Populate the names menu under a category."""
        names = [item["name"] for item in self.data if item["category"] == category]

        for name in names:
            category_menu.add_command(
                label=name, command=lambda n=name: self.select_item(n)
            )

    def select_item(self, name):
        """Handle item selection."""
        self.selected_item.set(f"Selected: {name}")

# Run the app
if __name__ == "__main__":
    app = NestedDropdownMenuApp()
    app.mainloop()
