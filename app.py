import objc
from PyQt6.QtCore import QCameraPermission, Qt
from PyQt6.QtWidgets import QWidget, QLabel, QMainWindow, QPushButton, QLabel, QVBoxLayout, QApplication
from Interface import Main_Window

NSBundle = objc.lookUpClass("NSBundle") # type: ignore
bundle = NSBundle.mainBundle()
info = bundle.localizedInfoDictionary() or bundle.infoDictionary()
info["NSCameraUsageDescription"] = "Camera access is required."

class App(QApplication):
    def __init__(self, argv: list[str]):
        super().__init__(argv)
        self.window = Main_Window()

    def get_camera_permission(self) -> Qt.PermissionStatus:
        permission = QCameraPermission()
        status = self.checkPermission(permission)

        if status == Qt.PermissionStatus.Undetermined:
            return instance.requestPermission(permission, self.on_permission_result) # type: ignore

        return status

    def on_permission_result(self, permission: QCameraPermission) -> Qt.PermissionStatus:
        return self.checkPermission(permission)