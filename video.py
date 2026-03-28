from PyQt6.QtWidgets import QLabel, QPushButton

from CameraAI.ai_vision import VisionManager
from PyQt6.QtCore import QTimer, pyqtSignal as Signal

class VideoFeed(QLabel):
    record_gesture_status = Signal(bool)

    def __init__(self, frame_width: int, frame_height: int):
        super().__init__()
        self.active = False
        self.frame_width = frame_width
        self.frame_height = frame_height

        self.frame_timer = QTimer()
        self.frame_timer.setInterval(int(1000/60))
        self.frame_timer.timeout.connect(self._update)
        self.setFixedSize(frame_width, frame_height)
        self.setScaledContents(True)
        self.vision = VisionManager.instance()

        self.record_gesture_button = QPushButton("Record Gesture")

    def _update(self):
        pxmap = self.vision.update_frame()
        if pxmap is not None:
            self.setPixmap(pxmap)

    def activate(self):
        self.active = True
        self.frame_timer.start()

    def deactivate(self):
        self.active = False
        self.frame_timer.stop()