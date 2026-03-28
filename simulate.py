from typing import Callable

from pynput.keyboard import Key
from pynput.keyboard import Controller as KeyboardController
import time
from datetime import datetime, timedelta
import threading
from pynput import keyboard
from queue import Queue

import threading


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
    def __init__(self, key: Key):
        self.key = key
        self.timestamp = datetime.now()

    def show_key(self) -> str:
        """NOT ALL KEYS HAVE CHAR ATTRIBUTE (Please use this method)"""
        try:
            return self.key.char
        except AttributeError:
            return str(self.key)


class Recorder:
    def __init__(self, duration: float):
        self.duration = duration
        self.recorded = Queue()

    def get_queue(self):
        return self.recorded

    def _press(self, key: Key, callback: Callable[[Key], None]):
        self.recorded.append(KeyPressEvent(key))
        cal

    def record(self, duration: timedelta , callback: Callable):
        last_press = datetime.now()

        def update_delta():
            nonlocal last_press
            last_press = datetime.now()

        listener = keyboard_controller.Listener(on_press=self._press, on_release=update_delta)
        listener.start()
        while last_press - datetime.now() < duration:
            time.sleep(0.1)

        listener.stop()





stop_flag = threading.Event()






# def display_results():
#     if not recorded_keys:
#         print("No keys were recorded.")
#         return
#
#     print(f"{'Time (s)':<12} {'Event':<10} {'Key'}")
#     print("-" * 35)
#
#     start_time = recorded_keys[0][0]
#     for ts, event, key in recorded_keys:
#         relative_time = ts - start_time
#         print(f"{relative_time:<12.3f} {event:<10} {key}")




#
# if __name__ == "__main__":
#     try:
#         duration = float(input("How many seconds to record? "))
#     except ValueError:
#         print("Invalid input. Using default of 5 seconds.")
#         duration = 5.0
#
#     record_keys(duration)
#     display_results()
#
# if __name__ == '__main__':
#     start()
#     while True:
#         time.sleep(1)
#         skip()