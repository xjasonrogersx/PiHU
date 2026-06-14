
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
import time
from pathlib import Path

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition

import paho.mqtt.client as mqtt


BASE_DIR = Path(__file__).resolve().parents[1]
GUI_DIR = Path(__file__).resolve().parent

image_list = [
    str(BASE_DIR / 'images' / '1775206919136.png'),  # car right
    str(BASE_DIR / 'images' / '1775206081435.png'),  # car middle
    str(BASE_DIR / 'images' / '1775205902337.png'),  # PiHU logo
]

# Radio station logos directory
LOGO_DIR = str(BASE_DIR / 'images' / 'RadioStationLogos' / 'RadioStationLogos_128x128_2026-04-08')
DEFAULT_LOGO = None  # Will be set to a placeholder or None

mqtt_broker = "localhost"
mqtt_port = 1883
mqtt_topic_dab_current = "car/dab/current_programme"
mqtt_topic_dab_seek = "car/dab/seek"
mqtt_topic_bg = "car/HU/bg_image"
mqtt_topic_gui_cmd = "car/HU/gui/cmd"
FONT_PATH = GUI_DIR / 'resources' / 'Montserrat' / 'Montserrat-VariableFont_wght.ttf'


def close_gui(*_args):
    app = App.get_running_app()
    if app is not None:
        app.stop()


def make_left_button(text, y, color, callback, font_size='14sp', width=0.38):
    button = Button(
        text=text,
        font_name='Montserrat',
        font_size=font_size,
        size_hint=(width, 0.09),
        pos_hint={'x': 0.05, 'y': y},
        background_color=color,
    )
    button.bind(on_press=callback)
    return button


class StartScreen(Screen):
    def __init__(self, **kwargs):
        super(StartScreen, self).__init__(**kwargs)

        root = FloatLayout()

        with root.canvas.before:
            Color(0, 0, 0, 0.35)
            self.top_bar = Rectangle(pos=(0, Window.height * 0.86), size=(Window.width, Window.height * 0.14))

        def _update_top_bar(*_args):
            self.top_bar.pos = (0, Window.height * 0.86)
            self.top_bar.size = (Window.width, Window.height * 0.14)

        Window.bind(size=_update_top_bar)

        bg = Image(
            source=image_list[2],
            allow_stretch=True,
            keep_ratio=False,
            size_hint=(1, 1),
            pos_hint={'x': 0, 'y': 0},
        )
        root.add_widget(bg)

        title = Label(
            text='PiHU',
            font_name='Montserrat',
            font_size='46sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint=(1, 0.2),
            pos_hint={'center_x': 0.5, 'top': 0.92},
        )
        root.add_widget(title)

        subtitle = Label(
            text='Car Head Unit',
            font_name='Montserrat',
            font_size='18sp',
            color=(0.9, 0.9, 0.9, 1),
            size_hint=(1, 0.12),
            pos_hint={'center_x': 0.5, 'top': 0.74},
        )
        root.add_widget(subtitle)

        self.clock_label = Label(
            text='--:--',
            font_name='Montserrat',
            font_size='30sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint=(0.28, 0.08),
            pos_hint={'right': 0.97, 'top': 0.98},
            halign='right',
            valign='middle',
        )
        self.clock_label.bind(size=self.clock_label.setter('text_size'))
        root.add_widget(self.clock_label)
        self.clock_subtitle = Label(
            text='Home',
            font_name='Montserrat',
            font_size='14sp',
            color=(0.9, 0.9, 0.9, 1),
            size_hint=(0.16, 0.05),
            pos_hint={'right': 0.97, 'top': 0.89},
            halign='right',
            valign='middle',
        )
        self.clock_subtitle.bind(size=self.clock_subtitle.setter('text_size'))
        root.add_widget(self.clock_subtitle)
        Clock.schedule_interval(self.update_clock, 1)

        root.add_widget(make_left_button('Open Radio', 0.48, (0.12, 0.55, 0.9, 1), self.open_radio, font_size='22sp', width=0.34))
        root.add_widget(make_left_button('Open CanBus', 0.32, (0.2, 0.55, 0.35, 1), self.open_canbus, font_size='22sp', width=0.34))
        root.add_widget(make_left_button('Exit GUI', 0.16, (0.7, 0.15, 0.15, 1), close_gui, font_size='18sp', width=0.34))

        self.add_widget(root)

    def open_radio(self, _instance):
        self.manager.current = 'radio'

    def open_canbus(self, _instance):
        self.manager.current = 'canbus'

    def update_clock(self, _dt):
        self.clock_label.text = time.strftime('%H:%M')


class RadioScreen(Screen):
    def __init__(self, **kwargs):
        super(RadioScreen, self).__init__(**kwargs)
        self.add_widget(OverlayWindow())


class CanBusScreen(Screen):
    def __init__(self, **kwargs):
        super(CanBusScreen, self).__init__(**kwargs)

        root = FloatLayout()
        bg = Image(
            source=image_list[1],
            allow_stretch=True,
            keep_ratio=False,
            size_hint=(1, 1),
            pos_hint={'x': 0, 'y': 0},
        )
        root.add_widget(bg)

        title = Label(
            text='CanBus',
            font_name='Montserrat',
            font_size='42sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint=(1, 0.2),
            pos_hint={'center_x': 0.5, 'top': 0.9},
        )
        root.add_widget(title)

        status = Label(
            text='CanBus page placeholder',
            font_name='Montserrat',
            font_size='18sp',
            color=(0.95, 0.95, 0.95, 1),
            size_hint=(1, 0.12),
            pos_hint={'center_x': 0.5, 'top': 0.72},
        )
        root.add_widget(status)

        root.add_widget(make_left_button('Home', 0.26, (0.2, 0.2, 0.2, 0.95), self.go_home, font_size='18sp', width=0.34))
        root.add_widget(make_left_button('Open Radio', 0.15, (0.12, 0.55, 0.9, 1), self.go_radio, font_size='18sp', width=0.34))
        root.add_widget(make_left_button('Open CanBus', 0.04, (0.2, 0.55, 0.35, 1), self.go_canbus, font_size='18sp', width=0.34))

        self.add_widget(root)

    def go_home(self, _instance):
        self.manager.current = 'start'

    def go_radio(self, _instance):
        self.manager.current = 'radio'

    def go_canbus(self, _instance):
        self.manager.current = 'canbus'



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
            size_hint=(0.34, 0.92),
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
            size_hint=(0.64, 0.3),
            pos_hint={'center_x': 0.5, 'top': 0.98},
            allow_stretch=True,
            keep_ratio=True
        )

        # Station label (large)
        self.station_label = Label(
            text="No Station",
            font_name='Montserrat',
            font_size='18sp',
            bold=True,
            color=(1, 1, 1, 1),
            halign='center',
            valign='middle',
            size_hint=(1, 0.12),
            pos_hint={'center_x': 0.5, 'top': 0.64}
        )
        self.station_label.bind(size=self.station_label.setter('text_size'))

        # Station type/genre
        self.station_type = Label(
            text="Type: --",
            font_name='Montserrat',
            font_size='13sp',
            color=(1, 1, 0, 1),
            halign='center',
            size_hint=(1, 0.08),
            pos_hint={'center_x': 0.5, 'top': 0.5}
        )
        self.station_type.bind(size=self.station_type.setter('text_size'))

        # Ensemble name
        self.ensemble_label = Label(
            text="Ensemble: --",
            font_name='Montserrat',
            font_size='12sp',
            color=(0.8, 0.8, 0.8, 1),
            halign='center',
            size_hint=(1, 0.08),
            pos_hint={'center_x': 0.5, 'top': 0.41}
        )
        self.ensemble_label.bind(size=self.ensemble_label.setter('text_size'))

        # Bitrate and DAB+ status
        self.bitrate_label = Label(
            text="Bitrate: -- | DAB: --",
            font_name='Montserrat',
            font_size='12sp',
            color=(0.8, 0.8, 0.8, 1),
            halign='center',
            size_hint=(1, 0.08),
            pos_hint={'center_x': 0.5, 'top': 0.32}
        )
        self.bitrate_label.bind(size=self.bitrate_label.setter('text_size'))

        # Seek button
        self.seek_button = Button(
            text='⏭️ SEEK',
            font_name='Montserrat',
            font_size='15sp',
            size_hint=(0.8, 0.12),
            pos_hint={'center_x': 0.5, 'top': 0.2},
            background_color=(0.2, 0.6, 1, 1)
        )
        self.seek_button.bind(on_press=self.on_seek_press)

        self.home_button = make_left_button('Home', 0.04, (0.2, 0.2, 0.2, 0.9), self.on_home_press)

        self.canbus_button = make_left_button('CanBus', 0.15, (0.2, 0.45, 0.3, 0.95), self.on_canbus_press)

        self.sidebar.add_widget(self.station_logo)
        self.sidebar.add_widget(self.station_label)
        self.sidebar.add_widget(self.station_type)
        self.sidebar.add_widget(self.ensemble_label)
        self.sidebar.add_widget(self.bitrate_label)
        self.sidebar.add_widget(self.seek_button)
        self.sidebar.add_widget(self.home_button)
        self.sidebar.add_widget(self.canbus_button)
        self.add_widget(self.sidebar)

        # Current programme data
        self.current_programme = {}

        # Keyboard bindings
        Window.bind(on_key_down=self.on_key_down)

        # MQTT
        # paho-mqtt 2.x exposes CallbackAPIVersion, older versions do not.
        if hasattr(mqtt, 'CallbackAPIVersion'):
            self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
        else:
            self.mqtt_client = mqtt.Client()
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

    def on_home_press(self, _instance):
        app = App.get_running_app()
        if app is not None and hasattr(app, 'screen_manager'):
            app.screen_manager.current = 'start'

    def on_canbus_press(self, _instance):
        app = App.get_running_app()
        if app is not None and hasattr(app, 'screen_manager'):
            app.screen_manager.current = 'canbus'

    def load_background(self, image_path):
        if not os.path.isabs(image_path):
            image_path = str((BASE_DIR / image_path).resolve())
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
            client.subscribe(mqtt_topic_gui_cmd)
            print(f"Subscribed to: {mqtt_topic_dab_current}, {mqtt_topic_bg}, {mqtt_topic_gui_cmd}")
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
            elif msg.topic == mqtt_topic_gui_cmd:
                command = msg.payload.decode().strip().lower()
                if command == "home":
                    Clock.schedule_once(lambda dt: self.go_home())
                elif command == "back":
                    Clock.schedule_once(lambda dt: self.go_back())
        except Exception as e:
            print(f"Error processing message: {e}")

    def go_home(self):
        app = App.get_running_app()
        if app is not None and hasattr(app, 'screen_manager'):
            app.screen_manager.current = 'start'

    def go_back(self):
        app = App.get_running_app()
        if app is None or not hasattr(app, 'screen_manager'):
            return

        current = app.screen_manager.current
        if current == 'canbus':
            app.screen_manager.current = 'radio'
        else:
            app.screen_manager.current = 'start'

    def mqtt_connect(self):
        try:
            self.mqtt_client.connect(mqtt_broker, mqtt_port, keepalive=60)
            self.mqtt_client.loop_forever()
        except Exception as e:
            print(f"MQTT Connection Error: {e}")


class MyApp(App):
    def build(self):
        if FONT_PATH.exists():
            LabelBase.register(name='Montserrat', fn_regular=str(FONT_PATH))

        if "--fullscreen" in sys.argv:
            Window.fullscreen = 'auto'
        else:
            Window.size = (1024, 600)

        self.screen_manager = ScreenManager(transition=FadeTransition(duration=0.2))
        self.screen_manager.add_widget(StartScreen(name='start'))
        self.screen_manager.add_widget(RadioScreen(name='radio'))
        self.screen_manager.add_widget(CanBusScreen(name='canbus'))
        self.screen_manager.current = 'start'
        return self.screen_manager


if __name__ == '__main__':
    MyApp().run()