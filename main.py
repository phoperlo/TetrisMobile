from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout

class TetrisApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        label = Label(text='Тетрис Mobile\nAPK готовится!', font_size=40)
        button = Button(text='Начать игру', size_hint=(1, 0.5))
        layout.add_widget(label)
        layout.add_widget(button)
        return layout

if __name__ == '__main__':
    TetrisApp().run()
