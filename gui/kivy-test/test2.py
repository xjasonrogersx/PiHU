# test2.py - Kivy-based car HU overlay
#
# Changes from original:
# - Grey box moved to left: pos_hint={'right': 1} -> pos_hint={'x': 0.02},
#   height reduced to 80% (size_hint=(0.3, 0.8)) matching test3.py panel proportions
# - Rounded corners: Rectangle replaced with RoundedRectangle(radius=[20])
# - Large speed display: replaced plain sidebar label with a large 100sp yellow
#   speed number + 50sp "km/h" label below, both with black outlines via
#   outline_color/outline_width
# - Fullscreen mode: python test2.py --fullscreen enables it; Escape exits
# - MQTT: subscribes to car/speed (updates the number) and car/HU/bg_image
#   (switches background); thread-safe via Clock.schedule_once
# - Keyboard shortcuts: keys 1/2/3 publish to car/HU/bg_image to switch between
#   the 3 background images (same as test3.py)
# - Window size: defaults to 1024x800 when not in fullscreen

import sys
import threading

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle
from kivy.core.window import Window
from kivy.clock import Clock
import paho.mqtt.client as mqtt

image_list = [
    '../../images/1775206919136.png',  # car right
    '../../PiHU/images/1775206081435.png',  # car middle
    '../../PiHU/images/1775205902337.png',  # PiHU logo
]

mqtt_broker = "localhost"
mqtt_port = 1883
mqtt_topic_speed = "car/speed"
mqtt_topic_bg = "car/HU/bg_image"


class OverlayWindow(FloatLayout):
    def __init__(self, **kwargs):
        super(OverlayWindow, self).__init__(**kwargs)

        # Background image
        self.bg_image = Image(
            source=image_list[0],
            allow_stretch=True,
            keep_ratio=False,
            size_hint=(1, 1),
            pos_hint={'x': 0, 'y': 0}
        )
        self.add_widget(self.bg_image)

        # Sidebar on the LEFT, 30% wide, 80% tall, vertically centred
        self.sidebar = FloatLayout(
            size_hint=(0.3, 0.8),
            pos_hint={'x': 0.02, 'center_y': 0.5}
        )
        self.sidebar.bind(size=self.update_rect, pos=self.update_rect)

        with self.sidebar.canvas.before:
            Color(0.5, 0.5, 0.5, 0.6)
            self.rect = RoundedRectangle(
                size=self.sidebar.size,
                pos=self.sidebar.pos,
                radius=[20]
            )

        # Large speed number – yellow with black outline
        self.speed_label = Label(
            text="???",
            font_size='100sp',
            bold=True,
            color=(1, 1, 0, 1),
            outline_color=(0, 0, 0),
            outline_width=4,
            halign='center',
            valign='middle',
            pos_hint={'center_x': 0.5, 'center_y': 0.58}
        )
        self.speed_label.bind(size=self.speed_label.setter('text_size'))

        # "km/h" label below the speed number
        self.kmh_label = Label(
            text="km/h",
            font_size='50sp',
            bold=True,
            color=(1, 1, 0, 1),
            outline_color=(0, 0, 0),
            outline_width=3,
            halign='center',
            valign='middle',
            pos_hint={'center_x': 0.5, 'center_y': 0.38}
        )
        self.kmh_label.bind(size=self.kmh_label.setter('text_size'))

        self.sidebar.add_widget(self.speed_label)
        self.sidebar.add_widget(self.kmh_label)
        self.add_widget(self.sidebar)

        # Keyboard bindings
        Window.bind(on_key_down=self.on_key_down)

        # MQTT
        self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_message = self.on_mqtt_message
        mqtt_thread = threading.Thread(target=self.mqtt_connect, daemon=True)
        mqtt_thread.start()

    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def update_speed(self, speed_text):
        self.speed_label.text = speed_text

    def load_background(self, image_path):
        self.bg_image.source = image_path
        self.bg_image.reload()

    def on_key_down(self, window, key, scancode, codepoint, modifier):
        if codepoint == '1':
            self.mqtt_client.publish(mqtt_topic_bg, '0')
        elif codepoint == '2':
            self.mqtt_client.publish(mqtt_topic_bg, '1')
        elif codepoint == '3':
            self.mqtt_client.publish(mqtt_topic_bg, '2')
        elif key == 27:  # Escape – exit fullscreen
            Window.fullscreen = False

    def on_mqtt_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT broker")
            client.subscribe(mqtt_topic_speed)
            client.subscribe(mqtt_topic_bg)
            print(f"Subscribed to: {mqtt_topic_speed}, {mqtt_topic_bg}")
        else:
            print(f"Failed to connect, return code {rc}")

    def on_mqtt_message(self, client, userdata, msg):
        try:
            if msg.topic == mqtt_topic_speed:
                speed = msg.payload.decode().strip()
                Clock.schedule_once(lambda dt: self.update_speed(speed))
            elif msg.topic == mqtt_topic_bg:
                bg_index = msg.payload.decode().strip()
                try:
                    index = int(bg_index)
                    if 0 <= index < len(image_list):
                        Clock.schedule_once(lambda dt: self.load_background(image_list[index]))
                    else:
                        print(f"Invalid image index: {index}. Must be 0-{len(image_list) - 1}")
                except ValueError:
                    Clock.schedule_once(lambda dt: self.load_background(bg_index))
        except Exception as e:
            print(f"Error processing message: {e}")

    def mqtt_connect(self):
        try:
            self.mqtt_client.connect(mqtt_broker, mqtt_port, keepalive=60)
            self.mqtt_client.loop_forever()
        except Exception as e:
            print(f"MQTT Connection Error: {e}")


class MyApp(App):
    def build(self):
        if "--fullscreen" in sys.argv:
            Window.fullscreen = 'auto'
        else:
            Window.size = (1024, 800)
        return OverlayWindow()


if __name__ == '__main__':
    MyApp().run()