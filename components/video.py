from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel, QPushButton

from CameraAI.ai_vision import VisionManager
from PyQt6.QtCore import QTimer, pyqtSignal as Signal, QThread


class VideoWorker(QThread):
    frame_ready = Signal(QPixmap)

    def __init__(self):
        super().__init__()
        self.vision = VisionManager().instance()
        self.active = False

    def run(self):
        self.active = True
        while self.active:
            pxmap = self.vision.update_frame()
            if pxmap:
                self.frame_ready.emit(pxmap)

    def stop(self):
        self.active = False


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

        self._worker = VideoWorker()
        self._worker.frame_ready.connect(self._update)

    def _update(self, frame: QPixmap | None):
        if frame is not None:
            self.setPixmap(frame)

    def activate(self):
        self._worker.start()

    def deactivate(self):
        self._worker.stop()