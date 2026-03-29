from PyQt6.QtWidgets import QWidget, QMainWindow, QPushButton, QLabel, QGridLayout, QListWidget, QListWidgetItem, QHBoxLayout, QLineEdit
from PyQt6.QtCore import Qt
from PyQt6.QtMultimedia import QCamera, QMediaCaptureSession
from PyQt6.QtGui import QIcon, QFont, QColor
from PyQt6.QtGui import QIcon
from components.gesture_map import GestureMap
from components.video import VideoFeed
from ShortcutPlayer import ShortcutPlayer
from components.camera_selector import CameraSelector


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Short Signs")
        central = QWidget()
        self.setStyleSheet("background-color: #1f1f1f")


        self.setCentralWidget(central)
        layout = QGridLayout(central)
        self.setStyleSheet("background-color: #1c1c1c")
        #app icon
        self.setWindowIcon(QIcon("components/skeleton_left.png"))

        #title
        self.title = QLabel("Short Signs")
        self.title_font = QFont('Sitka Display', 20)
        self.title.setFont(self.title_font)
        layout.addWidget(self.title, 0, 0)

        # video
        self.video_feed = VideoFeed(800, 600)
        layout.addWidget(self.video_feed, 1, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        # start feed
        self.start = QPushButton("Start feed")
        self.start.setFixedSize(100,100)
        layout.addWidget(self.start, 5, 0)
        self.session = QMediaCaptureSession()
        self.start.clicked.connect(self.video_feed.activate)
        start_font = QFont('Times New Roman')
        self.start.setFont(start_font)


        #adding the boxes on the side or smth
        self.gesture_map = GestureMap()
        self.gesture_map.signal_comit.connect(lambda: self.sliding_boxes(layout, self.gesture_map))
        self.sliding_boxes(layout, self.gesture_map)
        self.camera_select = CameraSelector(self.video_feed)
        self.camera_select.setFixedSize(300,300)
        container = QWidget()
        container_layout = QHBoxLayout(container)
        container_layout.addWidget(self.camera_select, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(container, 4, 1)

        self.video_feed.activate()

        #shortcut player loop
        self.shortcut_player = ShortcutPlayer(self.gesture_map.binding)

    def sliding_boxes(self, layout, gesture_map):
        box_layout = QListWidget()

        add_button = QPushButton("Add shortcut")
        add_button.setFixedSize(100,100)
        button_font = QFont('Times New Roman')
        add_button.setFont(button_font)
        for bind in gesture_map.binding.values():
            item = QListWidgetItem()
            item.setSizeHint(bind.sizeHint())
            box_layout.addItem(item)
            box_layout.setItemWidget(item, bind)
            bind.deleted.connect(lambda name, i=item: (
                box_layout.takeItem(box_layout.row(i))
            ))

        # Button container
        button_container = QWidget()
        container_layout = QHBoxLayout(button_container)
        container_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)  # align the layout itself
        container_layout.addWidget(gesture_map)


        button_item = QListWidgetItem()
        box_layout.addItem(button_item)
        box_layout.setItemWidget(button_item, button_container)

        # Force a proper size hint after the widget is set
        button_container.adjustSize()
        button_item.setSizeHint(button_container.sizeHint())

        layout.addWidget(box_layout, 1, 1)