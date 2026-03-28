import json

from typing import cast, Union

import numpy as np
from PyQt6.QtCore import QTimer, QEvent, Qt, QObject
from PyQt6.QtWidgets import QWidget, QApplication, QPushButton, QVBoxLayout, QLabel, QLineEdit
from PyQt6.QtCore import pyqtSignal as Signal
from CameraAI.ai_vision import VisionManager


class BuildGesture:
    def __init__(
            self,
            name: str | None = None,
            gesture: np.ndarray | None = None,
            shortcut: list[str] | None = None,
    ):
        self.name = name
        self.gesture = gesture
        self.shortcut = shortcut

    def reset_gesture(self):
        self.name = None
        self.gesture = None
        self.shortcut = None

    def set_name(self, name: str) -> "BuildGesture":
        self.name = name
        return self

    def set_gesture(self, gesture: np.ndarray) -> "BuildGesture":
        self.gesture = gesture
        return self

    def set_shortcut(self, shortcut: list[str]) -> "BuildGesture":
        self.shortcut = shortcut
        return self

    def all_set(self) -> bool:
        return (
            self.name is not None and
            self.gesture is not None and
            self.shortcut is not None

        )

    def reset(self):
        self.name = None
        self.gesture = None
        self.shortcut = None

class Gesture:
    def __init__(self, name: str, gesture: np.ndarray, shortcut: list[str]):
        self.name = name
        self.gesture = gesture
        self.shortcut = shortcut
    @staticmethod
    def try_from_build_gesture(build_gesture: BuildGesture) -> Union["Gesture", None]:
        if build_gesture.all_set():
            return Gesture(
                cast(str, build_gesture.name),
                cast(np.ndarray, build_gesture.gesture),
                cast(list[str], build_gesture.shortcut)
            )
        return None



    def nice(self) -> dict:
        return {
            "name" : self.name,
            "gesture" : self.gesture.tolist(),
            "shortcut" : self.shortcut
        }

class GestureMap(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(400, 200)
        self.build_map = BuildGesture()
        self.capture_gesture = GestureCapture()
        self.capture_binding = BindingCapture()

        layout = QVBoxLayout()


        # UI
        ## name
        self.name_field = QLineEdit()
        self.name_field.setText("")
        self.name_field.textChanged.connect(self.build_map.set_name)
        layout.addWidget(self.name_field)

        ## keybind
        self.keybind_button = QPushButton("Bind")
        self.keybind_button.clicked.connect(self.capture_binding.activate)
        layout.addWidget(self.keybind_button)

        self.keys_label = QLabel("Keys pressed: (none)")
        self.capture_binding.update.connect(lambda texts : self.keys_label.setText(" ".join(texts)))
        self.capture_binding.binding.connect(lambda texts : self.build_map.set_shortcut)
        self.keys_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.keys_label.setStyleSheet("font-size: 14px; color: #555;")
        layout.addWidget(self.keys_label)

        ## gesture
        self.gesture_button = QPushButton("Capture Gesture")
        self.gesture_button.clicked.connect(self.capture_gesture.record_gesture)
        self.capture_gesture.binding.connect(lambda gesture : self.build_map.set_gesture)
        layout.addWidget(self.gesture_button)

        # total
        self.commit_button = QPushButton("Commit")
        self.commit_button.clicked.connect(self._commit)
        layout.addWidget(self.commit_button)

        self.setLayout(layout)

    def _commit(self):
        gesture_mapping = Gesture.try_from_build_gesture(self.build_map)
        if gesture_mapping is None:
            return

        # self._save_to_json()

        print("saving")

    @staticmethod
    def _save_to_json(self) -> bool:
        try:
            with open("maps.json", 'w') as f:
                json.dump(self.gestures, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving gestures to json: {e}")
            return False

    def _add_gesture(self) -> bool:
        if self.current_gesture is None or self.current_shortcut is None:
            return False

        self.gestures.append(BuildGesture(self.current_gesture, self.current_shortcut))
        return True

    @staticmethod
    def load_from_json(self) -> "GestureMap":
        try:
            with open("maps.json", 'r') as f:
                data = json.loads(f.read())
                print(data)
        except Exception as e:
            print(f"Error saving gestures to json: {e}")

class GestureCapture(QObject):
    binding = Signal(np.ndarray)
    def __init__(self):
        super().__init__()
        self.timer = QTimer()
        self.timer.timeout.connect(self._capture)

    def record_gesture(self):
        self.timer.start(3000)

    def _capture(self):
        vision = VisionManager.instance()
        frame = vision.get_frame()
        landmarks = vision.get_landmarkers(frame)
        gestures = vision.record_gesture(landmarks.hand_landmarks)
        self.binding.emit(gestures)

class BindingCapture(QObject):
    binding = Signal(list)
    update = Signal(list)
    def __init__(self):
        super().__init__()
        self.active = False
        self.timer = QTimer()
        self.current_binding = []
        self.timer.timeout.connect(self._send)
        QApplication.instance().installEventFilter(self)

    def activate(self):
        print("BINDING ACTIVE")
        self.active = True
        self.timer.start(3000)

    def _send(self):
        self.binding.emit(self.current_binding)
        self.current_binding = []
        self.active = False

    def eventFilter(self, watched_obj, event):
        if not self.timer.isActive():
            return super().eventFilter(watched_obj, event)

        if event.type() == QEvent.Type.KeyPress:
            if event.isAutoRepeat():
                return True

            key = BindingCapture._get_event_key(event)
            self.current_binding.append(key)
            print("PRESSED", key)
            self.update.emit(self.current_binding)

            return True

        return super().eventFilter(watched_obj, event)

    @staticmethod
    def _get_event_key(event: QEvent) -> str:
        assert event.type() == QEvent.Type.KeyPress
        key_text = event.text()
        if not key_text or key_text.isspace():
            return Qt.Key(event.key()).name
        else:
            return key_text