from typing import Callable

from pynput.keyboard import Key, KeyCode
from pynput.keyboard import Controller as KeyboardController
from datetime import datetime, timedelta
from pynput import keyboard
import time
from PyQt6.QtCore import QThread, pyqtSignal as Signal


keyboard_controller = KeyboardController()

def start():
    keyboard_controller.tap(Key.media_play_pause)

def stop():
    keyboard_controller.tap(Key.media_play_stop)

def skip():
    keyboard_controller.tap(Key.media_next)

def previous():
    keyboard_controller.tap(Key.media_previous)

class KeyPressEvent:
    def __init__(self, key: Key | KeyCode):
        self.key = key
        self.timestamp = datetime.now()

    def show_key(self) -> str:
        try:
            if isinstance(self.key, Key):
                return f"special: {self.key.name}"
            return self.key.char or f"vk:{self.key.vk}"
        except AttributeError:
            return "<?>"

class Recorder(QThread):
    progress = Signal(KeyPressEvent)
    finished = Signal(list)

    def __init__(self, duration: timedelta):
        super().__init__()
        self.duration = duration
        self.recorded = []

    def _press(self, key: Key | KeyCode | None):
        if key is None:
            return
        event = KeyPressEvent(key)
        self.progress.emit(event)
        self.recorded.append(event)

    def run(self):
        last_press = datetime.now()

        def update_last_press(_key: Key | KeyCode | None):
            nonlocal last_press
            last_press = datetime.now()

        with keyboard.Listener(on_press=self._press, on_release=update_last_press) as listener:
            listener.start()
            while datetime.now() - last_press < self.duration:
                time.sleep(0.1)

        self.finished.emit(self.recorded)