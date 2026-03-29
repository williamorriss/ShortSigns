from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel, QPushButton
from PyQt6.QtCore import pyqtSignal as Signal, QThread
import time

from CameraAI.ai_vision import VisionManager


class VideoWorker(QThread):
    frame_ready = Signal(QPixmap)

    def __init__(self):
        super().__init__()
        self.vision = VisionManager.instance()  # fix: use singleton correctly
        self.active = False

    def run(self):
        self.active = True
        while self.active:
            pxmap = self.vision.update_frame()
            if pxmap:
                self.frame_ready.emit(pxmap)
            time.sleep(1 / 60)  # fix: ~60fps cap, don't burn CPU

    def stop(self):
        self.active = False
        self.wait()  # fix: block until thread actually finishes


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

        self._worker = VideoWorker()
        self._worker.frame_ready.connect(self._update)  # single connection

    def _update(self, frame: QPixmap):
        self.setPixmap(frame)

    def activate(self):
        if not self._worker.isRunning():
            self._worker.start()

    def deactivate(self):
        if self._worker.isRunning():
            self._worker.stop()  # now blocks until thread exits safely