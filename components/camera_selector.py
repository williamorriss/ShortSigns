import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from CameraAI.ai_vision import VisionManager
from components.video import VideoFeed


import cv2

from components.video import VideoFeed


def get_active_cameras(max_index: int = 5) -> list[QPushButton]:
    """
    Probe camera indices 0..max_index-1 and return info for every one that opens.
    """
    cameras = []

    for index in range(max_index):
        cap = cv2.VideoCapture(index)

        if not cap.isOpened():
            cap.release()
            continue

        # Read one frame to confirm the camera is actually streaming
        ok, _ = cap.read()
        if not ok:
            cap.release()
            continue

        btn = QPushButton(str(index))
        btn.i = index
        cameras.append(btn)
        cap.release()

    return cameras

class CameraSelector(QWidget):
    def __init__(self, video: VideoFeed):
        super().__init__()
        self.selected: int = 0
        self._buttons: list[QPushButton] = get_active_cameras()
        self._build_ui()
        self.video_feed = video
        self._on_select(item=0)

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setSpacing(12)
        root.setContentsMargins(20, 20, 20, 20)

        # Scrollable button area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        self.button_layout = QVBoxLayout(container)
        self.button_layout.setSpacing(8)
        self.button_layout.setContentsMargins(0, 0, 0, 0)

        for btn in self._buttons:
            btn.setCheckable(True)
            btn.setFixedHeight(40)
            btn.setFont(QFont("Georgia", 11))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, i=btn.i: self._on_select(i))
            self._apply_style(btn, selected=False)
            self.button_layout.addWidget(btn)

        self.button_layout.addStretch()
        scroll.setWidget(container)
        root.addWidget(scroll)

        # Status label
        self.status = QLabel("Nothing selected")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status.setFont(QFont("Times New Roman", 11))
        self.status.setStyleSheet("color: #888; font-style: italic;")
        root.addWidget(self.status)

        self.setStyleSheet("background-color: black;")

    # ── Selection logic ──────────────────────────────────────────────────────

    def _on_select(self, item: int):
        for btn in self._buttons:
            btn.setChecked(False)
            self._apply_style(btn, selected=False)

        try:
            self.video_feed.deactivate()
            VisionManager.instance().set_source(item)
            self.video_feed.activate()
            self.selected = item
            btn = self._buttons[item]
            btn.setChecked(True)
            self._apply_style(btn, selected=True)
            self.status.setText(f"Selected: {item}")
            self.status.setStyleSheet("color: #2a6aba; font-style: normal; font-weight: bold;")
        except Exception as e:
            print("exp", e)
            return

    # ── Styling helpers ──────────────────────────────────────────────────────

    @staticmethod
    def _apply_style(btn: QPushButton, selected: bool):
        if selected:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2a6aba;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 0 16px;
                }
                QPushButton:hover { background-color: #1f54a0; }
            """)
        else:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: black;
                    color: #333;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    padding: 0 16px;
                }
                QPushButton:hover { background-color: #eef4ff; border-color: #2a6aba; }
            """)