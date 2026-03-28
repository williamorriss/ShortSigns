import sys
from typing import Callable
import objc


from PyQt6.QtCore import QCameraPermission, Qt
from PyQt6.QtWidgets import QApplication

NSBundle = objc.lookUpClass("NSBundle") # type: ignore
bundle = NSBundle.mainBundle()
info = bundle.localizedInfoDictionary() or bundle.infoDictionary()
info["NSCameraUsageDescription"] = "Camera access is required."

class App(QApplication):
    _instance = None
    def __new__(cls, argv: list[str]):
        if cls._instance is None:
            cls._instance = super().__new__(cls, argv)
        return cls._instance

    def __init__(self, argv: list[str]):
        from Interface import MainWindow
        super().__init__(argv)
        self.window = MainWindow()
        self.window.show()
        self.exec()

    @classmethod
    def instance(cls) -> "App":
        return super().instance() # type: ignore

    def try_camera(self, callback: Callable):
        permission = QCameraPermission()
        status = self.checkPermission(permission)

        if status == Qt.PermissionStatus.Undetermined:
            self.requestPermission(
                permission,
                lambda p : self.on_permission_result(p, callback)
            )

        callback(status)

    def on_permission_result(self, permission: QCameraPermission, callback: Callable):
        status = self.checkPermission(permission)
        callback(status)

if __name__ == "__main__":
    app = App([sys.executable, __file__])