#!/usr/bin/env python3

import sys
import types
import unittest
from pathlib import Path
from unittest.mock import MagicMock, call


sys.path.insert(0, str(Path(__file__).resolve().parent))

if "paho.mqtt.client" not in sys.modules:
	paho_module = types.ModuleType("paho")
	mqtt_module = types.ModuleType("paho.mqtt")
	client_module = types.ModuleType("paho.mqtt.client")

	class _FakeClient:
		def __init__(self, *args, **kwargs) -> None:
			self.on_connect = None
			self.on_disconnect = None
			self.on_message = None

		def publish(self, *args, **kwargs):
			return None

	client_module.Client = _FakeClient
	mqtt_module.client = client_module
	paho_module.mqtt = mqtt_module
	sys.modules["paho"] = paho_module
	sys.modules["paho.mqtt"] = mqtt_module
	sys.modules["paho.mqtt.client"] = client_module

import pihu_man


class PiHUManagerTests(unittest.TestCase):
	def test_virtual_button_bands_match_observed_centers(self) -> None:
		self.assertEqual(
			pihu_man.VIRTUAL_BUTTON_Y_BANDS,
			(
				("power", 0, 139),
				("home", 140, 218),
				("back", 219, 305),
				("volume_up", 306, 390),
				("volume_down", 391, None),
			),
		)

	def test_virtual_button_action_mapping(self) -> None:
		manager = pihu_man.PiHUManager()

		self.assertEqual(manager._get_virtual_button_action(104), "power")
		self.assertEqual(manager._get_virtual_button_action(175), "home")
		self.assertEqual(manager._get_virtual_button_action(262), "back")
		self.assertEqual(manager._get_virtual_button_action(348), "volume_up")
		self.assertEqual(manager._get_virtual_button_action(433), "volume_down")

	def test_home_and_back_publish_gui_commands(self) -> None:
		manager = pihu_man.PiHUManager()
		manager.mqtt_client = MagicMock()

		manager._handle_virtual_button("home", 1065, 175)
		manager._handle_virtual_button("back", 1065, 262)

		self.assertEqual(
			manager.mqtt_client.publish.call_args_list,
			[
				call(pihu_man.TOPIC_GUI_CMD, "home", qos=0, retain=False),
				call(pihu_man.TOPIC_GUI_CMD, "back", qos=0, retain=False),
			],
		)

	def test_volume_buttons_step_wpctl_volume(self) -> None:
		manager = pihu_man.PiHUManager()
		manager._run_quick_command = MagicMock(return_value=True)

		manager._handle_virtual_button("volume_up", 1063, 348)
		manager._handle_virtual_button("volume_down", 1063, 433)

		self.assertEqual(
			manager._run_quick_command.call_args_list,
			[
				call(["wpctl", "set-mute", "@DEFAULT_AUDIO_SINK@", "0"]),
				call(
					[
						"wpctl",
						"set-volume",
						"@DEFAULT_AUDIO_SINK@",
						f"{pihu_man.VIRTUAL_BUTTON_VOLUME_STEP}+",
					]
				),
				call(["wpctl", "set-mute", "@DEFAULT_AUDIO_SINK@", "0"]),
				call(
					[
						"wpctl",
						"set-volume",
						"@DEFAULT_AUDIO_SINK@",
						f"{pihu_man.VIRTUAL_BUTTON_VOLUME_STEP}-",
					]
				),
			],
		)

	def test_power_button_only_publishes_status(self) -> None:
		manager = pihu_man.PiHUManager()
		manager._publish_status = MagicMock()
		manager.mqtt_client = MagicMock()

		manager._handle_virtual_button("power", 1067, 104)

		manager._publish_status.assert_called_once_with(
			"virtual_power_button",
			{"button": "power", "x": 1067, "y": 104},
		)
		manager.mqtt_client.publish.assert_not_called()


if __name__ == "__main__":
	unittest.main()
