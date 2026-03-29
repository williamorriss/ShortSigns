import json

import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel, QLineEdit
from PyQt6.QtCore import pyqtSignal as Signal
from components.capture.gesture import GestureCapture
from CameraAI.ai_vision import Gesture

from components.bindings import BindingManager
from components.capture.shortcut import BindingCapture, ShortCut

from components.binding_entry import BuildGestureEntry
type StoredGesture = list[int]


type StoredBinding = dict[str, dict[str, StoredBinding | ShortCut]]

class GestureMap(QWidget):
    signal_comit = Signal()

    def __init__(self):
        super().__init__()
        self.binding: BindingManager = BindingManager()
        self.binding.load_from_json()
        self.setFixedSize(400, 200)
        self.build_binding = BuildGestureEntry()
        self.capture_gesture = GestureCapture()
        self.capture_binding = BindingCapture()

        layout = QVBoxLayout()

        # UI
        ## name
        self.name_field = QLineEdit()
        self.name_field.setText("Input the name of the keybind here")
        self.name_field.textChanged.connect(self.build_binding.set_name)
        layout.addWidget(self.name_field)
        name_font = QFont('Times New Roman')
        self.name_field.setFont(name_font)

        ## keybind
        self.keybind_button = QPushButton("Bind")
        self.keybind_button.clicked.connect(self.capture_binding.activate)
        layout.addWidget(self.keybind_button)
        keybind_font = QFont('Times New Roman')
        self.keybind_button.setFont(keybind_font)

        self.keys_label = QLabel("Keys pressed: (none)")
        self.capture_binding.update.connect(lambda texts : self.keys_label.setText(" ".join(texts)))
        self.capture_binding.binding.connect(self.build_binding.set_shortcut)
        self.keys_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.keys_label.setStyleSheet("font-size: 14px; color: #555;")
        keylabel_font = QFont('Times New Roman')
        self.keys_label.setFont(keylabel_font)


        self.QLabel = QLabel("website:")
        self.QLabel.setFont(keylabel_font)
        layout.addWidget(self.QLabel)

        self.website_entry = QLineEdit()
        self.website_entry.setText("")
        self.website_entry.textChanged.connect(self.keys_label.setText)
        self.website_entry.textChanged.connect(lambda x : self.build_binding.set_shortcut([x]))
        name_font = QFont('Times New Roman')
        self.website_entry.setFont(name_font)
        layout.addWidget(self.website_entry)
        layout.addWidget(self.keys_label)

        self.key_status = QLabel()
        self.capture_binding.update.connect(self._set_shortcut_status)
        keystatus_font = QFont('Times New Roman')
        self.key_status.setFont(keystatus_font)

        ## gesture
        self.gesture_status = QLabel()
        self.capture_gesture.binding.connect(self._set_gesture_status)
        layout.addWidget(self.gesture_status)
        gesturestatus_font = QFont('Times New Roman')
        self.gesture_status.setFont(gesturestatus_font)

        self.gesture_button = QPushButton("Capture Gesture")
        self.gesture_button.clicked.connect(self.capture_gesture.record_gesture)
        self.capture_gesture.binding.connect(self.build_binding.set_gesture)
        layout.addWidget(self.gesture_button)
        gesture_font = QFont('Times New Roman')
        self.gesture_button.setFont(gesture_font)

        # total
        self.commit_button = QPushButton("Commit")
        self.commit_button.clicked.connect(self._commit)
        commit_font = QFont('Times New Roman')
        self.commit_button.setFont(commit_font)
        layout.addWidget(self.commit_button)

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
            self.build_binding.add_to_manager(self.binding)
            self.signal_comit.emit()
        except Exception as e:
            return