from bindings import GestureMap, Gesture
from CameraAI.ai_vision import VisionManager

from pynput.keyboard import Controller, Key

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QWidget

class ShortcutPlayer(QWidget):
    def __init__(self, gesture_map: GestureMap):
        super().__init__()

        self.hide()

        self.timer = QTimer()
        self.timer.timeout.connect(self.regonise_play_shortcut)
        self.timer.start(10)

        self.keyboard = Controller()
        self.gesture_map = gesture_map
        self.vision_manager = VisionManager.instance()

    def regonise_play_shortcut(self):
        frame = self.vision_manager.get_frame()
        landmarkers = self.vision_manager.get_landmarkers(frame)
        name, confidence = self.vision_manager.recognise_gesture(self.gesture_map.gestures, landmarkers.hand_landmarks)

        gesture: Gesture = self.gesture_map.get_gesture(name)
        if gesture is None:
            return

        print(f"Name: {name}, Gesture: {gesture.gesture}, Shortcut: {gesture.shortcut}")
        self._play_shortcut(gesture.shortcut)

    def _play_shortcut(self, shortcut: list[str]):
        for k in shortcut:
            if len(k) == 1:
                self.keyboard.press(k)
                self.keyboard.release(k)
            else:
                special = getattr(Key, k, None)
                if special:
                    self.keyboard.press(special)
                    self.keyboard.release(special)