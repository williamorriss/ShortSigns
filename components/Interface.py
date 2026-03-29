from PyQt6.QtWidgets import QWidget, QMainWindow, QPushButton, QLabel, QGridLayout, QListWidget, QListWidgetItem, \
    QHBoxLayout, QLineEdit, QGroupBox, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtMultimedia import QCamera, QMediaCaptureSession
from PyQt6.QtGui import QIcon
from components.gesture_map import GestureMap
from components.video import VideoFeed


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


        #adding the boxes on the side or smth
        self.sliding_boxes(layout)

        self.video_feed.activate()



    def sliding_boxes(self, layout):
        box_layout = QListWidget()
        gesture_map = GestureMap()

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

    def add_shortcut(self):
        row = QWidget()
        row_layout = QHBoxLayout(row)

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