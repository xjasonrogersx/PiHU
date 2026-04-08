# test3.py - Kivy-based DAB Radio HU display
#
# Features:
# - Subscribes to car/dab/current_programme MQTT topic
# - Displays DAB radio station logo (128x128) from RadioStationLogos directory
# - Shows station info: label, type, ensemble, bitrate, DAB+ status
# - Seek/Skip button to publish media control commands
# - Fullscreen mode: python test3.py --fullscreen enables it; Escape exits
# - Background image support for testing
# - Thread-safe MQTT updates via Clock.schedule_once
# - Window size: defaults to 1024x800 when not in fullscreen

import sys
import threading
import json
import os

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle
from kivy.core.window import Window
from kivy.clock import Clock
import paho.mqtt.client as mqtt


image_list = [
    '../../images/1775206919136.png',  # car right
    '../../PiHU/images/1775206081435.png',  # car middle
    '../../PiHU/images/1775205902337.png',  # PiHU logo
]

# Radio station logos directory
LOGO_DIR = '../../images/RadioStationLogos/RadioStationLogos_128x128_2026-04-08/'
DEFAULT_LOGO = None  # Will be set to a placeholder or None

mqtt_broker = "localhost"
mqtt_port = 1883
mqtt_topic_dab_current = "car/dab/current_programme"
mqtt_topic_dab_seek = "car/dab/seek"
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

        # Station logo (128x128)
        self.station_logo = Image(
            source='',
            size_hint=(0.5, 0.3),
            pos_hint={'center_x': 0.5, 'top': 1},
            allow_stretch=True,
            keep_ratio=True
        )

        # Station label (large)
        self.station_label = Label(
            text="No Station",
            font_size='20sp',
            bold=True,
            color=(1, 1, 1, 1),
            halign='center',
            valign='middle',
            size_hint=(1, 0.12),
            pos_hint={'center_x': 0.5, 'top': 0.65}
        )
        self.station_label.bind(size=self.station_label.setter('text_size'))

        # Station type/genre
        self.station_type = Label(
            text="Type: --",
            font_size='14sp',
            color=(1, 1, 0, 1),
            halign='center',
            size_hint=(1, 0.08),
            pos_hint={'center_x': 0.5, 'top': 0.52}
        )
        self.station_type.bind(size=self.station_type.setter('text_size'))

        # Ensemble name
        self.ensemble_label = Label(
            text="Ensemble: --",
            font_size='12sp',
            color=(0.8, 0.8, 0.8, 1),
            halign='center',
            size_hint=(1, 0.08),
            pos_hint={'center_x': 0.5, 'top': 0.43}
        )
        self.ensemble_label.bind(size=self.ensemble_label.setter('text_size'))

        # Bitrate and DAB+ status
        self.bitrate_label = Label(
            text="Bitrate: -- | DAB: --",
            font_size='12sp',
            color=(0.8, 0.8, 0.8, 1),
            halign='center',
            size_hint=(1, 0.08),
            pos_hint={'center_x': 0.5, 'top': 0.34}
        )
        self.bitrate_label.bind(size=self.bitrate_label.setter('text_size'))

        # Seek button
        self.seek_button = Button(
            text='⏭️ SEEK',
            font_size='16sp',
            size_hint=(0.8, 0.12),
            pos_hint={'center_x': 0.5, 'top': 0.22},
            background_color=(0.2, 0.6, 1, 1)
        )
        self.seek_button.bind(on_press=self.on_seek_press)

        self.sidebar.add_widget(self.station_logo)
        self.sidebar.add_widget(self.station_label)
        self.sidebar.add_widget(self.station_type)
        self.sidebar.add_widget(self.ensemble_label)
        self.sidebar.add_widget(self.bitrate_label)
        self.sidebar.add_widget(self.seek_button)
        self.add_widget(self.sidebar)

        # Current programme data
        self.current_programme = {}

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

    def find_logo(self, station_label):
        """
        Find the station logo in RadioStationLogos directory.
        Converts spaces to dashes and tries to match filename.
        Returns full path if found, empty string otherwise.
        """
        if not station_label:
            return ''
        
        # Convert spaces to dashes for filename matching
        logo_name = station_label.replace(' ', '-') + '.png'
        logo_path = os.path.join(LOGO_DIR, logo_name)
        
        if os.path.exists(logo_path):
            return logo_path
        
        print(f"Logo not found: {logo_path}")
        return ''

    def update_station_display(self, programme_data):
        """Update sidebar display with station information"""
        try:
            # Extract service info
            service = programme_data.get('service', {})
            station_label = service.get('label', 'Unknown')
            station_type = programme_data.get('type', '--')
            ensemble = programme_data.get('ensemble', '--')
            bitrate = programme_data.get('bitrate', '--')
            dab_plus = programme_data.get('dab_plus', 0)
            
            # Update labels
            self.station_label.text = station_label
            self.station_type.text = f"Type: {station_type}"
            self.ensemble_label.text = f"Ensemble: {ensemble}"
            dab_status = "DAB+" if dab_plus else "DAB"
            self.bitrate_label.text = f"Bitrate: {bitrate} kbps | {dab_status}"
            
            # Find and load logo
            logo_path = self.find_logo(station_label)
            if logo_path:
                self.station_logo.source = logo_path
                self.station_logo.reload()
            
            print(f"Updated display for: {station_label}")
        except Exception as e:
            print(f"Error updating station display: {e}")

    def on_seek_press(self, instance):
        """Publish seek/skip command"""
        self.mqtt_client.publish(mqtt_topic_dab_seek, '1')
        print("Seek/Skip published")

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
            client.subscribe(mqtt_topic_dab_current)
            client.subscribe(mqtt_topic_bg)
            print(f"Subscribed to: {mqtt_topic_dab_current}, {mqtt_topic_bg}")
        else:
            print(f"Failed to connect, return code {rc}")

    def on_mqtt_message(self, client, userdata, msg):
        try:
            if msg.topic == mqtt_topic_dab_current:
                # Parse JSON message
                payload = msg.payload.decode().strip()
                programme_data = json.loads(payload)
                self.current_programme = programme_data
                Clock.schedule_once(lambda dt: self.update_station_display(programme_data))
                print(f"Received programme update: {programme_data.get('service', {}).get('label', 'Unknown')}")
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