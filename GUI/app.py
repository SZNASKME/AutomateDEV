from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.treeview import TreeView
from kivy.uix.treeview import TreeViewLabel
from kivy.uix.modalview import ModalView

class MyApp(App):
    def build(self):
        self.label = Label(text="Hello, World!")
        button = Button(text="Click Me")
        button.bind(on_press=self.on_button_click)
        
        treeview = TreeView(root_options=dict(text='Tree One'))
        treeview.add_node(TreeViewLabel(text='Child One'))
        treeview.add_node(TreeViewLabel(text='Child Two'))
        treeview.add_node(TreeViewLabel(text='Child Three'))   
        
        
        
        
        
        
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(self.label)
        layout.add_widget(button)
        layout.add_widget(treeview)
        
        return layout

    def on_button_click(self, instance):
        self.label.text = "Button Clicked!"

if __name__ == '__main__':
    MyApp().run()
