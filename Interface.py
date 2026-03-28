import threading
from queue import Queue

import cv2
from PyQt6.QtGui import QPainter, QImage, QFont
from PyQt6.QtWidgets import QWidget, QMainWindow, QPushButton, QLabel, QGridLayout, QApplication, QListWidget, QListWidgetItem, QHBoxLayout
from PyQt6.QtCore import Qt, QPoint, QTimer
from PyQt6.QtMultimedia import QCamera, QMediaCaptureSession, QMediaDevices
from PyQt6.QtMultimediaWidgets import QVideoWidget
from keyboard import Recorder
from datetime import timedelta
from CameraAI.ai_vision import VisionManager

from app import App


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Short Signs")
        central = QWidget()
        self.setCentralWidget(central)
        layout = QGridLayout(central)

        #title
        self.title = QLabel("Short Signs")
        self.title_font = self.title.font()
        self.title_font.setPointSize(20)
        self.title.setFont(self.title_font)
        layout.addWidget(self.title, 0, 0)

        # video
        self.camera = None
        self.video_feed = QVideoWidget()
        self.video_feed.setFixedSize(800,500)
        layout.addWidget(self.video_feed, 1, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        # start feed
        self.start = QPushButton("Start feed")
        self.start.setFixedSize(100,100)
        layout.addWidget(self.start, 2, 0)
        self.session = QMediaCaptureSession()
        self.start.clicked.connect(self.start_video)

        # bindings
        self.recorder = Recorder(duration=timedelta(seconds=5))
        layout.addWidget(self.recorder, 2, 1)

        # camera
        self.vision = VisionManager()

        #adding the boxes on the side or smth
        self.sliding_boxes(layout)

    def sliding_boxes(self,layout):
        #the item is so that the button can be added into the list widget
        self.box_layout = QListWidget()
        item = QListWidgetItem(self.box_layout)

        add_button = QPushButton("Add shortcut")
        add_button.setFixedSize(100,100)
        add_button.clicked.connect(self.add_shortcut)

        #this is so the add button can be centered
        button_container = QWidget()
        container_layout = QHBoxLayout(button_container)
        container_layout.addWidget(add_button, alignment=Qt.AlignmentFlag.AlignHCenter)

        item.setSizeHint(button_container.sizeHint())
        self.box_layout.addItem(item)
        self.box_layout.setItemWidget(item,button_container)

        layout.addWidget(self.box_layout, 1, 1)

    def add_shortcut(self):
        row = QWidget()
        row_layout = QHBoxLayout(row)
        gesture = QLabel("Gesture")
        shortcut = QPushButton("Shortcut")
        name = QLabel("Name")
        gesture.setFixedSize(100,50)
        shortcut.setFixedSize(100,50)
        name.setFixedSize(100,50)
        row_layout.addWidget(name)
        row_layout.addWidget(shortcut)
        row_layout.addWidget(gesture)
        
        item = QListWidgetItem()
        item.setSizeHint(row.sizeHint())
        # insert before the last item (the button)
        button_index = self.box_layout.count() - 1
        self.box_layout.insertItem(button_index, item)
        self.box_layout.setItemWidget(item, row)




    def start_video(self):
        self.timer = QTimer(self)


        self.timer.timeout.connect(self.set_image())
        self.timer.start(10)


    def set_image(self):
        self.video_feed.setImage(self.vision.get_frame())


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

class Video(QImage):
    def __init__(self, vision: VisionManager):
        super().__init__()
        self.vision = vision
        self.buffer = Queue()

    def get_frames(self):
        self.buffer.put(self.vision.get_frame())

    def set_frame(self, image):
        self.image = image
        self.setMinimumSize(image.size())
        self.update()