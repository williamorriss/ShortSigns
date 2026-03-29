from PyQt6.QtWidgets import QWidget, QMainWindow, QPushButton, QLabel, QGridLayout, QListWidget, QListWidgetItem, QHBoxLayout, QLineEdit
from PyQt6.QtCore import Qt
from PyQt6.QtMultimedia import QCamera, QMediaCaptureSession
from PyQt6.QtGui import QIcon
from bindings import GestureMap
from video import VideoFeed


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Short Signs")
        central = QWidget()

        self.setCentralWidget(central)
        layout = QGridLayout(central)
        #app icon
        self.setWindowIcon(QIcon("skeleton_left.png"))

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
        layout.addWidget(self.start, 3, 0)
        self.session = QMediaCaptureSession()
        self.start.clicked.connect(self.video_feed.activate)

        self.gesture_map = GestureMap()
        layout.addWidget(self.gesture_map, 2, 1)

        #adding the boxes on the side or smth
        self.sliding_boxes(layout)

        self.video_feed.activate()

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
        name = QLineEdit("Name")

        shortcut.setFixedSize(100,50)
        name.setFixedSize(100,50)
        row_layout.addWidget(name)
        row_layout.addWidget(shortcut)

        item = QListWidgetItem()
        item.setSizeHint(row.sizeHint())
        # insert before the last item (the button)
        button_index = self.box_layout.count() - 1
        self.box_layout.insertItem(button_index, item)
        self.box_layout.setItemWidget(item, row)