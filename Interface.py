from PyQt6.QtWidgets import QWidget, QMainWindow, QPushButton, QGridLayout
from PyQt6.QtCore import Qt
from PyQt6.QtMultimedia import QMediaCaptureSession
import threading

from PyQt6.QtWidgets import QWidget, QMainWindow, QPushButton, QLabel, QGridLayout, QApplication, QListWidget, QListWidgetItem
from PyQt6.QtCore import Qt, QPoint, QTimer
from PyQt6.QtMultimedia import QCamera, QMediaCaptureSession, QMediaDevices
from bindings import GestureMap
from video import VideoFeed
from ShortcutPlayer import ShortcutPlayer


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
        self.video_feed = VideoFeed(800, 600)
        layout.addWidget(self.video_feed, 1, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        # start feed
        self.start = QPushButton("Start feed")
        self.start.setFixedSize(100,100)
        layout.addWidget(self.start, 2, 0)
        self.session = QMediaCaptureSession()
        self.start.clicked.connect(self.video_feed.activate)

        self.gesture_map = GestureMap()
        layout.addWidget(self.gesture_map, 2, 1)

        #adding the boxes on the side or smth
        self.sliding_boxes(layout)

        self.video_feed.activate()

        #shortcut player loop
        self.shortcut_player = ShortcutPlayer(self.gesture_map)
        layout.addWidget(self.shortcut_player, 2, 2)

    def sliding_boxes(self,layout):
        box_layout = QListWidget()
        item = QListWidgetItem(box_layout)
        add_button = QPushButton("Add shortcut")
        add_button.setFixedSize(100,100)
        box_layout.addItem(item)
        box_layout.setItemWidget(item,add_button)

        layout.addWidget(box_layout, 1, 1)