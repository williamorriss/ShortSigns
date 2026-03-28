from pynput.keyboard import Key, KeyCode
from pynput.keyboard import Controller as KeyboardController
from pynput import keyboard
from datetime import datetime, timedelta
from PyQt6.QtCore import QObject, QTimer, pyqtSignal as Signal, QElapsedTimer, QEvent
from PyQt6.QtWidgets import QPushButton, QLabel
import threading
from app import App

keyboard_controller = KeyboardController()

def start():    keyboard_controller.tap(Key.media_play_pause)
def stop():     keyboard_controller.tap(Key.media_play_stop)
def skip():     keyboard_controller.tap(Key.media_next)
def previous(): keyboard_controller.tap(Key.media_previous)

from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QKeyEvent


class Recorder(QWidget):
    def __init__(self, duration: timedelta):
        super().__init__()
        App.instance().installEventFilter(self)

        self._timer = QTimer()
        self._timer.timeout.connect(self._finish)

        self.duration = duration
        self.keys_pressed = []

        self.setWindowTitle("Keyboard Listener")
        self.setFixedSize(400, 200)

        # UI

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self._start)

        self.status_label = QLabel(f"Listening  seconds...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("font-size: 18px; font-weight: bold;")

        self.keys_label = QLabel("Keys pressed: (none)")
        self.keys_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.keys_label.setStyleSheet("font-size: 14px; color: #555;")

        layout = QVBoxLayout()
        layout.addWidget(self.start_button)
        layout.addWidget(self.status_label)
        layout.addWidget(self.keys_label)
        self.setLayout(layout)


    def eventFilter(self, watched_obj, event):
        if not self._timer.isActive():
            return super().eventFilter(watched_obj, event)


        if event.type() == QEvent.Type.KeyPress:
            if event.isAutoRepeat():
                return True

            key_text = event.text()

            if not key_text or key_text.isspace():
                key_name = Qt.Key(event.key()).name
            else:
                key_name = key_text

            self.keys_pressed.append(key_name)
            display = ", ".join(self.keys_pressed[-10:])
            self.keys_label.setText(f"Keys pressed: {display}")

            return True

        return super().eventFilter(watched_obj, event)

    def _start(self):
        print("start")
        self._timer.start(self.duration.seconds * 1000)

    def _finish(self):
        self._timer.stop()
        print(self.keys_pressed)
        print("finished")

    def _tick(self):
        elapsed =  timedelta(milliseconds=self.timer.elapsed())
        delta   = self.duration - elapsed
        remaining_s = max(delta / 1000, 0.0)

        if delta.seconds > 0:
            self.status_label.setText(f"Listening for {remaining_s:.1f} seconds...")
        else:
            self.timer.restart()