from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout

class MyApp(App):
    def build(self):
        self.label = Label(text="Hello, World!")
        button = Button(text="Click Me")
        button.bind(on_press=self.on_button_click)
        
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(self.label)
        layout.add_widget(button)
        
        return layout

    def on_button_click(self, instance):
        self.label.text = "Button Clicked!"

if __name__ == '__main__':
    MyApp().run()
