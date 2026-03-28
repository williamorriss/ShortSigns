import sys
from PyQt6.QtWidgets import QWidget, QMainWindow, QPushButton, QLabel, QVBoxLayout, QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtMultimedia import QCamera, QMediaCaptureSession, QMediaDevices
from PyQt6.QtMultimediaWidgets import QVideoWidget


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

  def start_video(self):
    device = QMediaDevices.defaultVideoInput()
    self.camera = QCamera(device)
    self.session.setCamera(self.camera)
    self.session.setVideoOutput(self.video_feed)
    self.camera.start()

app = QApplication(sys.argv)
window = Main_Window()
window.show()
app.exec()



