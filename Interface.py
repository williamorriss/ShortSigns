from PyQt6.QtWidgets import QWidget, QMainWindow, QPushButton, QLabel, QGridLayout, QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtMultimedia import QCamera, QMediaCaptureSession, QMediaDevices
from PyQt6.QtMultimediaWidgets import QVideoWidget
from keyboard import Recorder
from datetime import timedelta

from app import App


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main window")
        central = QWidget()

        self.setCentralWidget(central)
        layout = QGridLayout(central)

        # video
        self.camera = None
        self.video_feed = QVideoWidget()
        self.video_feed.setFixedSize(800,500)
        layout.addWidget(self.video_feed, 0, 1)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        # start feed
        self.start = QPushButton("Start feed")
        self.start.setFixedSize(100,100)
        layout.addWidget(self.start, 1, 1)
        self.session = QMediaCaptureSession()
        self.start.clicked.connect(self.start_video)

        # bindings
        self.recorder = Recorder(duration=timedelta(seconds=5))
        layout.addWidget(self.recorder, 2, 1)

    def start_video(self):
        app = App.instance()
        app.try_camera(self.cam)


    def cam(self, permission: Qt.PermissionStatus):
        if permission != Qt.PermissionStatus.Granted:
            print("Access denied")
            return

        device = QMediaDevices.defaultVideoInput()

        if device.isNull():
            print("No camera device detected.")
            return

        self.camera = QCamera(device)
        self.session.setCamera(self.camera)
        self.session.setVideoOutput(self.video_feed)
        self.camera.start()