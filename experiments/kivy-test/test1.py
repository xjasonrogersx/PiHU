from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle

class OverlayWindow(FloatLayout):
    def __init__(self, **kwargs):
        super(OverlayWindow, self).__init__(**kwargs)

        # 1. Add the Background Image
        # Replace 'background.jpg' with your actual file path
        self.bg_image = Image(
            source='/workspace/PiHU/images/1775206081435.png', 
            allow_stretch=True, 
            keep_ratio=False,
            size_hint=(1, 1),
            pos_hint={'x': 0, 'y': 0}
        )
        self.add_widget(self.bg_image)

        # 2. Create the Sidebar Container
        # We use a RelativeLayout or simple Widget to hold the canvas drawing
        self.sidebar = FloatLayout(
            size_hint=(0.3, 1), 
            pos_hint={'right': 1, 'y': 0}
        )
        
        # Bind the update_rect function to resize the box if the window changes
        self.sidebar.bind(size=self.update_rect, pos=self.update_rect)

        with self.sidebar.canvas.before:
            # Set color to Grey (0.5, 0.5, 0.5) with 0.6 opacity
            Color(0.5, 0.5, 0.5, 0.6)
            self.rect = Rectangle(size=self.sidebar.size, pos=self.sidebar.pos)

        # 3. Add Text to the Sidebar
        # 'font_name' can be a path to a .ttf file if you want a specific "letter" font
        self.label = Label(
            text="This is your\nsidebar text.",
            font_size='20sp',
            color=(1, 1, 1, 1),
            halign='center',
            valign='middle',
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        # Ensure text alignment works by binding texture size
        self.label.bind(size=self.label.setter('text_size'))
        
        self.sidebar.add_widget(self.label)
        self.add_widget(self.sidebar)

    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

class MyApp(App):
    def build(self):
        return OverlayWindow()

if __name__ == '__main__':
    MyApp().run()