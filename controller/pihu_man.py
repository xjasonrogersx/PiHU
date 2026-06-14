#!/usr/bin/env python3
"""PiHU background manager.

Responsibilities:
- Keep GUI process running (auto-restart on crash/exit).
- Keep OpenAuto process running (auto-restart on crash/exit).
- Connect to MQTT and handle runtime commands.
- Start/stop DAB process on MQTT request.
- Handle audio sink selection and volume control.
- Monitor optional GT911 side-strip virtual buttons from raw evdev events.
"""

from __future__ import annotations

import json
import logging
import os
import shlex
import signal
import subprocess
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import paho.mqtt.client as mqtt

try:
	from evdev import InputDevice, ecodes  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - depends on target runtime package
	InputDevice = None
	ecodes = None


LOG_LEVEL = os.getenv("PIHU_LOG_LEVEL", "INFO").upper()
MQTT_HOST = os.getenv("PIHU_MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("PIHU_MQTT_PORT", "1883"))


def _env_flag(name: str, default: bool) -> bool:
	value = os.getenv(name)
	if value is None:
		return default
	return value.strip().lower() in {"1", "true", "yes", "on"}

BASE_DIR = Path(__file__).resolve().parents[1]

GUI_CWD = Path(os.getenv("PIHU_GUI_CWD", str(BASE_DIR / "gui")))
GUI_CMD = shlex.split(os.getenv("PIHU_GUI_CMD", "python3 pihu_gui.py --fullscreen"))

OPENAUTO_CWD = Path(os.getenv("PIHU_OPENAUTO_CWD", str(Path.home())))
OPENAUTO_CMD = shlex.split(os.getenv("PIHU_OPENAUTO_CMD", "/usr/bin/autoapp --log_level info"))
OPENAUTO_LD_LIBRARY_PATH = os.path.expanduser(
	os.getenv("PIHU_OPENAUTO_LD_LIBRARY_PATH", "~/.")
)

DAB_CWD = Path(os.getenv("PIHU_DAB_CWD", str(BASE_DIR)))
DAB_CMD = shlex.split(
	os.getenv("PIHU_DAB_CMD", "./build/dab/dab-radio/dab_tuner_aac")
)

TOPIC_MANAGER_STATUS = "car/HU/manager/status"
TOPIC_MANAGER_CMD = "car/HU/manager/cmd"
TOPIC_GUI_CMD = "car/HU/gui/cmd"
TOPIC_OPENAUTO_CMD = "car/HU/openauto/cmd"
TOPIC_DAB_CMD = "car/HU/dab/cmd"
TOPIC_VOLUME = "car/HU/volume"
TOPIC_AUDIO_SELECT = "car/HU/audio/select"
OPENAUTO_WINDOW_TITLE = os.getenv("PIHU_OPENAUTO_WINDOW_TITLE", "autoapp")

VIRTUAL_BUTTONS_ENABLED = _env_flag("PIHU_VIRTUAL_BUTTONS_ENABLED", True)
VIRTUAL_BUTTON_EVENT_DEVICE = os.getenv(
	"PIHU_VIRTUAL_BUTTON_EVENT_DEVICE", "/dev/input/event4"
)
VIRTUAL_BUTTON_MIN_X = int(os.getenv("PIHU_VIRTUAL_BUTTON_MIN_X", "1040"))
VIRTUAL_BUTTON_DEBOUNCE_S = float(os.getenv("PIHU_VIRTUAL_BUTTON_DEBOUNCE_S", "0.35"))
VIRTUAL_BUTTON_VOLUME_STEP = os.getenv("PIHU_VIRTUAL_BUTTON_VOLUME_STEP", "5%")
VIRTUAL_BUTTON_ACTIONS = (
	"power",
	"home",
	"back",
	"volume_up",
	"volume_down",
)
VIRTUAL_BUTTON_Y_CENTERS = (104, 175, 262, 348, 433)


def _build_virtual_button_bands(
	actions: Tuple[str, ...], centers: Tuple[int, ...]
) -> Tuple[Tuple[str, int, Optional[int]], ...]:
	if len(actions) != len(centers):
		raise ValueError("virtual button actions/centers length mismatch")

	bands = []
	lower = 0
	for index, action in enumerate(actions):
		upper = None
		if index < len(centers) - 1:
			upper = (centers[index] + centers[index + 1]) // 2
		bands.append((action, lower, upper))
		if upper is not None:
			lower = upper + 1
	return tuple(bands)


VIRTUAL_BUTTON_Y_BANDS = _build_virtual_button_bands(
	VIRTUAL_BUTTON_ACTIONS, VIRTUAL_BUTTON_Y_CENTERS
)


@dataclass
class ManagedProcess:
	name: str
	command: List[str]
	cwd: Path
	env_updates: Dict[str, str] = field(default_factory=dict)
	always_on: bool = False
	restart_delay_s: int = 3
	process: Optional[subprocess.Popen] = None
	last_exit_code: Optional[int] = None
	last_start_time: float = 0.0

	def is_running(self) -> bool:
		return self.process is not None and self.process.poll() is None

	def start(self) -> bool:
		if self.is_running():
			return False

		env = os.environ.copy()
		env.update(self.env_updates)

		logging.info("Starting %s: %s (cwd=%s)", self.name, self.command, self.cwd)
		self.process = subprocess.Popen(
			self.command,
			cwd=str(self.cwd),
			env=env,
			stdout=subprocess.DEVNULL,
			stderr=subprocess.DEVNULL,
		)
		self.last_start_time = time.time()
		return True

	def stop(self) -> bool:
		if not self.is_running():
			return False

		assert self.process is not None
		logging.info("Stopping %s (pid=%s)", self.name, self.process.pid)
		self.process.terminate()
		try:
			self.process.wait(timeout=8)
		except subprocess.TimeoutExpired:
			logging.warning("Force killing %s (pid=%s)", self.name, self.process.pid)
			self.process.kill()
			self.process.wait(timeout=4)

		self.last_exit_code = self.process.returncode
		return True

	def restart(self) -> None:
		self.stop()
		self.start()

	def update_exit_state(self) -> bool:
		if self.process is None:
			return False

		rc = self.process.poll()
		if rc is None:
			return False

		self.last_exit_code = rc
		logging.warning("Process %s exited with code %s", self.name, rc)
		self.process = None
		return True


class PiHUManager:
	def __init__(self) -> None:
		self.shutdown_event = threading.Event()
		self.lock = threading.Lock()

		self.processes: Dict[str, ManagedProcess] = {
			"gui": ManagedProcess(
				name="gui",
				command=GUI_CMD,
				cwd=GUI_CWD,
				always_on=True,
			),
			"openauto": ManagedProcess(
				name="openauto",
				command=OPENAUTO_CMD,
				cwd=OPENAUTO_CWD,
				env_updates={"LD_LIBRARY_PATH": OPENAUTO_LD_LIBRARY_PATH},
				always_on=True,
			),
			"dab": ManagedProcess(
				name="dab",
				command=DAB_CMD,
				cwd=DAB_CWD,
				always_on=False,
			),
		}

		self.dab_requested = False

		# paho-mqtt 2.x exposes CallbackAPIVersion, older versions do not.
		if hasattr(mqtt, "CallbackAPIVersion"):
			self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
		else:
			self.mqtt_client = mqtt.Client()
		self.mqtt_client.on_connect = self._on_connect
		self.mqtt_client.on_disconnect = self._on_disconnect
		self.mqtt_client.on_message = self._on_message
		self.virtual_button_thread: Optional[threading.Thread] = None

	def start(self) -> None:
		self._install_signal_handlers()
		self._start_always_on_processes()
		self._start_mqtt()
		self._start_virtual_button_monitor()

		supervisor_thread = threading.Thread(target=self._supervisor_loop, daemon=True)
		supervisor_thread.start()

		while not self.shutdown_event.is_set():
			time.sleep(0.5)

		self._shutdown()

	def _install_signal_handlers(self) -> None:
		def _handle_signal(signum, _frame):
			logging.info("Signal %s received, shutting down", signum)
			self.shutdown_event.set()

		signal.signal(signal.SIGINT, _handle_signal)
		signal.signal(signal.SIGTERM, _handle_signal)

	def _start_always_on_processes(self) -> None:
		with self.lock:
			for proc in self.processes.values():
				if proc.always_on:
					try:
						proc.start()
					except Exception:
						logging.exception("Failed to start %s", proc.name)

	def _start_mqtt(self) -> None:
		logging.info("Connecting MQTT to %s:%s", MQTT_HOST, MQTT_PORT)
		self.mqtt_client.connect_async(MQTT_HOST, MQTT_PORT, keepalive=30)
		self.mqtt_client.loop_start()

	def _start_virtual_button_monitor(self) -> None:
		if not VIRTUAL_BUTTONS_ENABLED:
			logging.info("Virtual buttons disabled by PIHU_VIRTUAL_BUTTONS_ENABLED")
			return
		if InputDevice is None or ecodes is None:
			logging.warning("Virtual buttons disabled: python3-evdev unavailable")
			return

		logging.info(
			"Virtual buttons enabled: device=%s min_x=%s debounce=%.2fs step=%s bands=%s",
			VIRTUAL_BUTTON_EVENT_DEVICE,
			VIRTUAL_BUTTON_MIN_X,
			VIRTUAL_BUTTON_DEBOUNCE_S,
			VIRTUAL_BUTTON_VOLUME_STEP,
			VIRTUAL_BUTTON_Y_BANDS,
		)

		self.virtual_button_thread = threading.Thread(
			target=self._virtual_button_loop,
			name="virtual-buttons",
			daemon=True,
		)
		self.virtual_button_thread.start()

	def _virtual_button_loop(self) -> None:
		open_error_logged = False
		while not self.shutdown_event.is_set():
			device = None
			try:
				logging.info("Opening virtual button device %s", VIRTUAL_BUTTON_EVENT_DEVICE)
				device = InputDevice(VIRTUAL_BUTTON_EVENT_DEVICE)
				open_error_logged = False
				logging.info("Monitoring virtual buttons on %s", VIRTUAL_BUTTON_EVENT_DEVICE)
				self._read_virtual_button_events(device)
			except (FileNotFoundError, PermissionError, OSError) as exc:
				if not open_error_logged:
					logging.warning(
						"Virtual buttons unavailable on %s: %s",
						VIRTUAL_BUTTON_EVENT_DEVICE,
						exc,
					)
					open_error_logged = True
			except Exception:
				logging.exception("Virtual button monitor failed")
			finally:
				if device is not None:
					device.close()

			if self.shutdown_event.wait(5):
				return

	def _read_virtual_button_events(self, device: Any) -> None:
		latest_x: Optional[int] = None
		latest_y: Optional[int] = None
		touch_active = False
		touch_triggered = False
		last_trigger_time = 0.0
		logging.info("Virtual button event loop active for %s", getattr(device, "path", VIRTUAL_BUTTON_EVENT_DEVICE))

		for event in device.read_loop():
			if self.shutdown_event.is_set():
				return

			if event.type == ecodes.EV_ABS:
				if event.code in (ecodes.ABS_MT_POSITION_X, ecodes.ABS_X):
					latest_x = event.value
					logging.debug("Virtual button ABS X=%s", latest_x)
				elif event.code in (ecodes.ABS_MT_POSITION_Y, ecodes.ABS_Y):
					latest_y = event.value
					logging.debug("Virtual button ABS Y=%s", latest_y)
				elif event.code == ecodes.ABS_MT_TRACKING_ID:
					if event.value == -1:
						touch_active = False
						touch_triggered = False
						logging.debug("Virtual button touch released via TRACKING_ID=-1")
					else:
						touch_active = True
						touch_triggered = False
						logging.debug("Virtual button touch active via TRACKING_ID=%s", event.value)
			elif event.type == ecodes.EV_KEY and event.code == ecodes.BTN_TOUCH:
				if event.value == 0:
					touch_active = False
					touch_triggered = False
					logging.debug("Virtual button BTN_TOUCH released")
				elif event.value == 1:
					touch_active = True
					logging.debug("Virtual button BTN_TOUCH pressed")
			elif event.type == ecodes.EV_SYN and event.code == ecodes.SYN_REPORT:
				logging.debug(
					"Virtual button SYN_REPORT x=%s y=%s active=%s triggered=%s",
					latest_x,
					latest_y,
					touch_active,
					touch_triggered,
				)
				if not touch_active or touch_triggered:
					logging.debug(
						"Virtual button ignored: touch_active=%s touch_triggered=%s",
						touch_active,
					touch_triggered,
					)
					continue
				if latest_x is None or latest_y is None or latest_x < VIRTUAL_BUTTON_MIN_X:
					logging.debug(
						"Virtual button ignored by position: x=%s y=%s min_x=%s",
						latest_x,
						latest_y,
						VIRTUAL_BUTTON_MIN_X,
					)
					continue

				now = time.monotonic()
				touch_triggered = True
				if now - last_trigger_time < VIRTUAL_BUTTON_DEBOUNCE_S:
					logging.info(
						"Virtual button debounced: x=%s y=%s delta=%.3fs",
						latest_x,
						latest_y,
						now - last_trigger_time,
					)
					continue

				action = self._get_virtual_button_action(latest_y)
				if action is None:
					logging.info(
						"Virtual button ignored: no action for y=%s bands=%s",
						latest_y,
						VIRTUAL_BUTTON_Y_BANDS,
					)
					continue

				last_trigger_time = now
				logging.info("Virtual button resolved to action=%s x=%s y=%s", action, latest_x, latest_y)
				self._handle_virtual_button(action, latest_x, latest_y)

	def _get_virtual_button_action(self, y_value: int) -> Optional[str]:
		for action, lower, upper in VIRTUAL_BUTTON_Y_BANDS:
			if y_value < lower:
				continue
			if upper is None or y_value <= upper:
				return action
		return None

	def _handle_virtual_button(self, action: str, x_value: int, y_value: int) -> None:
		logging.info("Virtual button %s", action)
		if action == "power":
			logging.info("Publishing virtual power event")
			self._publish_status(
				"virtual_power_button",
				{"button": action, "x": x_value, "y": y_value},
			)
		elif action == "home":
			logging.info("Publishing GUI home command")
			self.mqtt_client.publish(TOPIC_GUI_CMD, "home", qos=0, retain=False)
		elif action == "back":
			logging.info("Publishing GUI back command")
			self.mqtt_client.publish(TOPIC_GUI_CMD, "back", qos=0, retain=False)
		elif action == "volume_up":
			logging.info("Applying volume up step %s", VIRTUAL_BUTTON_VOLUME_STEP)
			self._step_volume("+")
		elif action == "volume_down":
			logging.info("Applying volume down step %s", VIRTUAL_BUTTON_VOLUME_STEP)
			self._step_volume("-")

	def _step_volume(self, direction: str) -> None:
		mute_cmd = ["wpctl", "set-mute", "@DEFAULT_AUDIO_SINK@", "0"]
		cmd = [
			"wpctl",
			"set-volume",
			"@DEFAULT_AUDIO_SINK@",
			f"{VIRTUAL_BUTTON_VOLUME_STEP}{direction}",
		]
		self._run_quick_command(mute_cmd)
		self._run_quick_command(cmd)

	def _on_connect(self, client, _userdata, _flags, rc):
		if rc != 0:
			logging.error("MQTT connection failed with code %s", rc)
			return

		topics = [
			(TOPIC_MANAGER_CMD, 0),
			(TOPIC_GUI_CMD, 0),
			(TOPIC_OPENAUTO_CMD, 0),
			(TOPIC_DAB_CMD, 0),
			(TOPIC_VOLUME, 0),
			(TOPIC_AUDIO_SELECT, 0),
		]
		for topic, qos in topics:
			client.subscribe(topic, qos=qos)

		logging.info("MQTT connected and subscribed to manager topics")
		self._publish_status("mqtt_connected")

	def _on_disconnect(self, _client, _userdata, rc):
		logging.warning("MQTT disconnected (rc=%s)", rc)

	def _on_message(self, _client, _userdata, msg):
		payload = msg.payload.decode(errors="ignore").strip()
		topic = msg.topic
		logging.info("MQTT message on %s: %s", topic, payload)

		try:
			if topic == TOPIC_MANAGER_CMD:
				self._handle_manager_command(payload)
			elif topic == TOPIC_GUI_CMD:
				self._handle_process_command("gui", payload)
			elif topic == TOPIC_OPENAUTO_CMD:
				self._handle_process_command("openauto", payload)
			elif topic == TOPIC_DAB_CMD:
				self._handle_dab_command(payload)
			elif topic == TOPIC_VOLUME:
				self._handle_volume(payload)
			elif topic == TOPIC_AUDIO_SELECT:
				self._handle_audio_select(payload)
		except Exception:
			logging.exception("Failed handling MQTT message topic=%s payload=%s", topic, payload)

	def _handle_manager_command(self, payload: str) -> None:
		cmd = payload.lower()
		if cmd == "restart_all":
			with self.lock:
				self.processes["gui"].restart()
				self.processes["openauto"].restart()
				if self.dab_requested:
					self.processes["dab"].restart()
			self._publish_status("restart_all")
		elif cmd == "status":
			self._publish_status("status_request")

	def _handle_process_command(self, name: str, payload: str) -> None:
		cmd = payload.lower()
		with self.lock:
			proc = self.processes[name]
			if cmd == "start":
				proc.start()
			elif cmd in {"focus", "show", "activate"} and name == "openauto":
				if not proc.is_running():
					proc.start()
				self._focus_openauto_window()
			elif cmd == "stop":
				proc.stop()
				proc.always_on = False
			elif cmd == "restart":
				proc.restart()
				if name in ("gui", "openauto"):
					proc.always_on = True

		self._publish_status(f"{name}_{cmd}")

	def _focus_openauto_window(self) -> None:
		commands = [
			["xdotool", "search", "--name", OPENAUTO_WINDOW_TITLE, "windowactivate", "--sync"],
			["wmctrl", "-a", OPENAUTO_WINDOW_TITLE],
		]
		for command in commands:
			if self._run_quick_command(command):
				logging.info("Focused OpenAuto using %s", command[0])
				return
		logging.warning(
			"Could not focus OpenAuto window '%s' (xdotool/wmctrl unavailable or window not found)",
			OPENAUTO_WINDOW_TITLE,
		)

	def _handle_dab_command(self, payload: str) -> None:
		cmd = payload.lower()
		with self.lock:
			dab = self.processes["dab"]
			if cmd == "start":
				self.dab_requested = True
				dab.start()
			elif cmd == "stop":
				self.dab_requested = False
				dab.stop()
			elif cmd == "restart":
				self.dab_requested = True
				dab.restart()

		self._publish_status(f"dab_{cmd}")

	def _handle_volume(self, payload: str) -> None:
		value = self._extract_volume_value(payload)
		if value is None:
			logging.warning("Invalid volume payload: %s", payload)
			return

		fraction = max(0.0, min(1.0, value / 100.0))
		cmd = ["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", f"{fraction:.2f}"]
		mute_cmd = ["wpctl", "set-mute", "@DEFAULT_AUDIO_SINK@", "0"]

		self._run_quick_command(mute_cmd)
		ok = self._run_quick_command(cmd)
		if ok:
			self._publish_status("volume_set", {"volume_percent": int(round(value))})

	def _handle_audio_select(self, payload: str) -> None:
		sink = payload
		if not sink:
			return

		# First try wpctl (works with sink ID or named sink), fallback to pw-metadata.
		ok = self._run_quick_command(["wpctl", "set-default", sink])
		if not ok:
			metadata = json.dumps({"name": sink})
			ok = self._run_quick_command(
				["pw-metadata", "-n", "settings", "0", "default.audio.sink", metadata]
			)

		if ok:
			self._publish_status("audio_sink_selected", {"sink": sink})

	def _extract_volume_value(self, payload: str) -> Optional[float]:
		try:
			parsed = json.loads(payload)
			if isinstance(parsed, dict):
				if "percent" in parsed:
					return float(parsed["percent"])
				if "volume" in parsed:
					return float(parsed["volume"])
			if isinstance(parsed, (int, float)):
				return float(parsed)
		except json.JSONDecodeError:
			pass

		try:
			return float(payload)
		except ValueError:
			return None

	def _run_quick_command(self, command: List[str]) -> bool:
		try:
			result = subprocess.run(
				command,
				stdout=subprocess.DEVNULL,
				stderr=subprocess.DEVNULL,
				timeout=5,
				check=False,
			)
			if result.returncode != 0:
				logging.warning("Command failed (%s): %s", result.returncode, command)
				return False
			return True
		except (FileNotFoundError, subprocess.TimeoutExpired):
			logging.warning("Command unavailable or timed out: %s", command)
			return False

	def _supervisor_loop(self) -> None:
		while not self.shutdown_event.is_set():
			self._supervise_processes()
			time.sleep(1)

	def _supervise_processes(self) -> None:
		with self.lock:
			for name, proc in self.processes.items():
				exited = proc.update_exit_state()

				should_run = proc.always_on or (name == "dab" and self.dab_requested)
				if not should_run:
					continue

				if proc.is_running():
					continue

				elapsed = time.time() - proc.last_start_time
				if elapsed < proc.restart_delay_s:
					continue

				try:
					proc.start()
					if exited:
						self._publish_status(f"{name}_restarted")
				except Exception:
					logging.exception("Failed to restart %s", name)

	def _publish_status(self, event: str, extra: Optional[Dict[str, object]] = None) -> None:
		status = {
			"event": event,
			"time": int(time.time()),
			"processes": {
				name: {
					"running": proc.is_running(),
					"pid": proc.process.pid if proc.process else None,
					"last_exit_code": proc.last_exit_code,
				}
				for name, proc in self.processes.items()
			},
			"dab_requested": self.dab_requested,
		}
		if extra:
			status.update(extra)

		self.mqtt_client.publish(TOPIC_MANAGER_STATUS, json.dumps(status), qos=0, retain=False)

	def _shutdown(self) -> None:
		logging.info("Stopping PiHU manager")
		self.mqtt_client.loop_stop()
		self.mqtt_client.disconnect()

		with self.lock:
			for proc in self.processes.values():
				try:
					proc.stop()
				except Exception:
					logging.exception("Failed stopping %s", proc.name)


def main() -> None:
	logging.basicConfig(
		level=getattr(logging, LOG_LEVEL, logging.INFO),
		format="%(asctime)s %(levelname)s %(message)s",
	)

	manager = PiHUManager()
	manager.start()


if __name__ == "__main__":
	main()
