from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel, QPushButton
from PyQt6.QtCore import pyqtSignal as Signal, QThread

from CameraAI.ai_vision import VisionManager, Frame

class VideoFeed(QLabel):
    record_gesture_status = Signal(bool)

    def __init__(self, frame_width: int, frame_height: int):
        super().__init__()
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.setFixedSize(frame_width, frame_height)
        self.setScaledContents(True)

        self.vision = VisionManager.instance()
        self.record_gesture_button = QPushButton("Record Gesture")

        self._worker = VisionManager.instance()
        self._worker.image_ready.connect(self._update)  # single connection
        self._worker.start()

    def _update(self, img: QPixmap):
        if img is not None:
            self.setPixmap(img)

    def activate(self):
        if not self._worker.isRunning():
            self._worker.start()

    def deactivate(self):
        if self._worker.isRunning():
            self._worker.stop()  # now blocks until thread exits safely