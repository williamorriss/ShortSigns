import sys
from PyQt6.QtWidgets import QWidget, QLabel, QMainWindow, QPushButton, QLabel, QVBoxLayout, QApplication
from PyQt6.QtCore import Qt, QCoreApplication
from PyQt6.QtGui import QFont
from PyQt6.QtCore import QCameraPermission
from PyQt6.QtMultimedia import QCamera, QMediaCaptureSession, QMediaDevices
from PyQt6.QtMultimediaWidgets import QVideoWidget

from simulate import Recorder, KeyPressEvent
from datetime import timedelta


class Main_Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main window")
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        self.video_feed = QVideoWidget()
        layout.addWidget(self.video_feed)
        self.start = QPushButton("Start feed")
        layout.addWidget(self.start)
        self.camera = None
        self.session = QMediaCaptureSession()

        self.start.clicked.connect(self.start_video)

    def _setup_and_start_camera(self):
        device = QMediaDevices.defaultVideoInput()

        if device.isNull():
            print("No camera device detected.")
            return

        self.camera = QCamera(device)
        self.session.setCamera(self.camera)
        self.session.setVideoOutput(self.video_feed)
        self.camera.start()



    def update_recording(self, event: KeyPressEvent):
        current_txt = self.recording_label.text()
        new_txt = current_txt + event.show_key()
        self.recording_label.setText(new_txt)


    def finish_recording(self):
        pass

app = QApplication(sys.argv)
window = Main_Window()
window.show()
app.exec()