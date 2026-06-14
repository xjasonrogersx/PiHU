#!/usr/bin/env python3
"""PiHU background manager.

Responsibilities:
- Keep GUI process running (auto-restart on crash/exit).
- Keep OpenAuto process running (auto-restart on crash/exit).
- Connect to MQTT and handle runtime commands.
- Start/stop DAB process on MQTT request.
- Handle audio sink selection and volume control.
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
from typing import Dict, List, Optional

import paho.mqtt.client as mqtt


LOG_LEVEL = os.getenv("PIHU_LOG_LEVEL", "INFO").upper()
MQTT_HOST = os.getenv("PIHU_MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("PIHU_MQTT_PORT", "1883"))

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

	def start(self) -> None:
		self._install_signal_handlers()
		self._start_always_on_processes()
		self._start_mqtt()

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
			elif cmd == "stop":
				proc.stop()
				proc.always_on = False
			elif cmd == "restart":
				proc.restart()
				if name in ("gui", "openauto"):
					proc.always_on = True

		self._publish_status(f"{name}_{cmd}")

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
