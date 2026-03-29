import json
from collections.abc import ValuesView
from json import JSONDecodeError

from PyQt6.QtCore import pyqtSignal as Signal
import numpy as np
from PyQt6.QtWidgets import QPushButton, QVBoxLayout, QLabel, QLineEdit, QGroupBox
from CameraAI.ai_vision import Gesture
from PyQt6.QtWidgets import QWidget
from components.capture.shortcut import ShortCut

type StoredGesture = list[int]

type BindingDict = dict[str, Binding]

type StoredBinding = dict[str, dict[str, StoredBinding | ShortCut]]

class BindingManager:
    def __init__(self):
        self.bindings: BindingDict = {}
        self.load_from_json()

    def delete_item(self, name: str):
        del self.bindings[name]
        self.save_to_json()

    def save_to_json(self):
        with open("maps.json", "w") as f:
            if not self.bindings:
                json.dump({}, f)
                return

            data = {}
            for k, v in self.bindings.items():
                data.update(v.to_stored())

            json.dump(data, f, indent=4)

    def values(self) -> ValuesView["Binding"]:
        return self.bindings.values()

    def add_value(self, binding: "Binding"):
        self.bindings[binding.name] = binding
        self.save_to_json()

    def load_from_json(self):
        try:
            data = json.load(open("maps.json"))
            for k, v in data.items():
                self.bindings[k] = Binding(name=k, gesture=v["gesture"], shortcut=v["shortcut"], manager=self)
            print(self.bindings)

        except FileNotFoundError:
            self.bindings = {}

        except JSONDecodeError:
            self.bindings = {}

class Binding(QWidget):
    deleted = Signal(object)
    def __init__(
        self,
        name: str,
        gesture: Gesture,
        shortcut: ShortCut,
        manager: BindingManager,
    ):
        super().__init__()
        self.name = name
        self.gesture = gesture
        self.shortcut = shortcut
        self.manager = manager

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)

        self.group = QGroupBox(name)
        group_layout = QVBoxLayout()
        display_shortcut = " ".join(self.shortcut)
        group_layout.addWidget(QLabel(display_shortcut))
        self.group.setLayout(group_layout)

        self.delete_button = QPushButton(f"Delete {self.name}")
        self.delete_button.clicked.connect(self._delete)

        root_layout.addWidget(self.group)
        root_layout.addWidget(self.delete_button)

    def _delete(self):
        self.manager.delete_item(self.name)
        self.deleted.emit(self.name)
        self.deleteLater()

    def to_stored(self) -> StoredBinding:
        return {
            self.name : {
                "gesture" : self.gesture.tolist(),
                "shortcut" : self.shortcut
            }
        }

    @staticmethod
    def from_stored(binding: StoredBinding) -> "Binding":
        new = Binding()
        for x in binding.keys(): # this is a singleton trust xxx
            new.name = x

        new.gesture = np.array(binding[new.name]["gesture"])
        new.shortcut = np.array(binding[new.name]["shortcut"])
        return new