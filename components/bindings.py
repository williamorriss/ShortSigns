import json
import os

import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel, QLineEdit
from capture.gesture import GestureCapture
from CameraAI.ai_vision import Gesture
from capture.shortcut import BindingCapture, ShortCut

from binding_entry import BuildGestureEntry
type StoredGesture = list[int]

type Binding = dict[str, dict[str, Gesture | ShortCut]]

type StoredBinding = dict[str, dict[str, StoredBinding | ShortCut]]

def to_stored_binding(binding: Binding) -> StoredBinding:
    return {
        name : {
            k : y.tolist() if k == "gesture" else y for k,y in x.items()
        } for name, x in binding.items()
    }

def to_programme_binding(binding: Binding) -> Binding:
    return {
        name : {
            k : np.array(y) if k == "gesture" else y for k,y in x.items()
        } for name, x in binding.items()
    }

def create_binding(build: BuildGestureEntry) -> Binding:
    if not build.all_set():
        raise Exception ("Not all set")
    return {
        build.name : {
            "gesture" : build.gesture,
            "shortcut" : build.shortcut
        }
    }


class GestureMap(QWidget):
    def __init__(self):
        super().__init__()
        self.binding: Binding = {}
        self._load_from_json()
        self.setFixedSize(400, 200)
        self.build_binding = BuildGestureEntry()
        self.capture_gesture = GestureCapture()
        self.capture_binding = BindingCapture()

        layout = QVBoxLayout()

        # UI
        ## name
        self.name_field = QLineEdit()
        self.name_field.setText("")
        self.name_field.textChanged.connect(self.build_binding.set_name)
        layout.addWidget(self.name_field)

        ## keybind
        self.keybind_button = QPushButton("Bind")
        self.keybind_button.clicked.connect(self.capture_binding.activate)
        layout.addWidget(self.keybind_button)

        self.keys_label = QLabel("Keys pressed: (none)")
        self.capture_binding.update.connect(lambda texts : self.keys_label.setText(" ".join(texts)))
        self.capture_binding.binding.connect(self.build_binding.set_shortcut)
        self.keys_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.keys_label.setStyleSheet("font-size: 14px; color: #555;")
        layout.addWidget(self.keys_label)

        self.key_status = QLabel()
        self.capture_binding.update.connect(self._set_shortcut_status)

        ## gesture
        self.gesture_button = QPushButton("Capture Gesture")
        self.gesture_button.clicked.connect(self.capture_gesture.record_gesture)
        self.capture_gesture.binding.connect(self.build_binding.set_gesture)
        layout.addWidget(self.gesture_button)

        self.gesture_status = QLabel()
        self.capture_gesture.binding.connect(self._set_gesture_status)
        layout.addWidget(self.gesture_status)

        # total
        self.commit_button = QPushButton("Commit")
        self.commit_button.clicked.connect(self._commit)
        layout.addWidget(self.commit_button)

        # load
        self.load_button = QPushButton("Load")
        self.load_button.clicked.connect(self._load_from_json)
        layout.addWidget(self.load_button)

        self.setLayout(layout)

    def _set_gesture_status(self, gesture: np.ndarray | None):
        if gesture is not None:
            self.gesture_status.setText("Gesture Set")
        else:
            self.gesture_status.setText("Failed to set Gesture")

    def _set_shortcut_status(self, shortcut: list[str] | None):
        if shortcut is not None:
            self.key_status.setText("Shortcut Set")
        else:
            self.key_status.setText("Failed to set Shortcut")

    def _commit(self):
        print("COMMIT")
        try:
            self.binding.update(create_binding(self.build_binding))
            print("saving")
            self._save_to_json()
        except Exception as e:
            return


    def _save_to_json(self):
        try:
            with open("maps.json", 'w') as f:
                stored = to_stored_binding(self.binding)
                json.dump(stored, f, indent=4)
        except Exception as e:
            print(f"Error saving gestures to json: {e}")
            return False

    def _load_from_json(self) -> Binding:
        try:
            with open("maps.json", 'r') as f:
                data = json.load(f)
                if data is None:
                    return {}
                self.binding = to_programme_binding(data)

        except Exception as e:
            print(f"Error loading gestures to json: {e}")
            return {}


def save_gestures_to_json(self, file_path=None):
    try:
        if file_path is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(script_dir, "saved_gestures.json")

        # Convert numpy arrays to lists for JSON serialization
        serializable_data = {}
        for gesture_name, gesture_data in self.saved_gestures.items():
            if isinstance(gesture_data, np.ndarray):
                serializable_data[gesture_name] = gesture_data.tolist()
            elif isinstance(gesture_data, dict):
                # Handle nested dictionaries (for multiple samples)
                serializable_data[gesture_name] = {}
                for key, value in gesture_data.items():
                    if isinstance(value, np.ndarray):
                        serializable_data[gesture_name][key] = value.tolist()
                    else:
                        serializable_data[gesture_name][key] = value
            else:
                serializable_data[gesture_name] = gesture_data

        with open(file_path, 'w') as f:
            json.dump(serializable_data, f, indent=4)
        print(f"Gestures saved to {file_path}")
        return True
    except Exception as e:
        print(f"Error saving gestures to json: {e}")
        return False

def load_gestures_from_json(self, file_path=None):
    try:
        if file_path is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(script_dir, "saved_gestures.json")

        with open(file_path, 'r') as f:
            loaded_data = json.load(f)

        # Convert lists back to numpy arrays
        self.saved_gestures = {}
        for gesture_name, gesture_data in loaded_data.items():
            if isinstance(gesture_data, list):
                # If it's a list, convert back to numpy array
                self.saved_gestures[gesture_name] = np.array(gesture_data)
            elif isinstance(gesture_data, dict):
                # If it's a dictionary, check for numpy arrays inside
                self.saved_gestures[gesture_name] = {}
                for key, value in gesture_data.items():
                    if isinstance(value, list):
                        self.saved_gestures[gesture_name][key] = np.array(value)
                    else:
                        self.saved_gestures[gesture_name][key] = value
            else:
                self.saved_gestures[gesture_name] = gesture_data

        print(f"Loaded {len(self.saved_gestures)} gestures from {file_path}")
        return True
    except FileNotFoundError:
        print(f"File {file_path} not found. Starting with empty gestures.")
        self.saved_gestures = {}
        return False
    except Exception as e:
        print(f"Error loading gestures from json: {e}")
        return False