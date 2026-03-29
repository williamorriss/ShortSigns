import sys
from typing import Callable

from PyQt6.QtCore import QCameraPermission, Qt
from PyQt6.QtWidgets import QApplication
from CameraAI.ai_vision import VisionManager
from components.Interface import MainWindow
from PyQt6.QtGui import QFont

def get_camera_permission(self):
    permission = QCameraPermission()
    status = self.checkPermission(permission)
    if status != Qt.PermissionStatus.Granted:
        self.requestPermission(permission, self.on_permission_result) # type

def on_permission_result(self, permission: QCameraPermission, callback: Callable):
    status = self.checkPermission(permission)
    if status != Qt.PermissionStatus.Granted:
        self.get_camera_permission()

if __name__ == "__main__":
    if sys.platform == "darwin":
        import objc
        NSBundle = objc.lookUpClass("NSBundle") # type: ignore
        bundle = NSBundle.mainBundle()
        info = bundle.localizedInfoDictionary() or bundle.infoDictionary()
        info["NSCameraUsageDescription"] = "Camera access is required."

    app = QApplication(sys.argv)
    app.setStyleSheet("""
        QLabel {color: #f0ead6}
                      """)
    window = MainWindow()
    window.show()
    get_camera_permission(app)
    app.exec()