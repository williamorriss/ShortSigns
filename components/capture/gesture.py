from copy import deepcopy
import numpy as np
from PyQt6.QtCore import QTimer, QObject
from PyQt6.QtCore import pyqtSignal as Signal
from CameraAI.ai_vision import VisionManager

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
        print("Setting Gesture", gestures)
        self.binding.emit(deepcopy(gestures))
        self.timer.stop()