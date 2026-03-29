from copy import deepcopy
from PyQt6.QtCore import QTimer, QEvent, Qt, QObject
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import pyqtSignal as Signal


type ShortCut = list[str]

class BindingCapture(QObject):
    binding = Signal(list)
    update = Signal(list)
    def __init__(self):
        super().__init__()
        self.timer = QTimer()
        self.current_binding = []
        self.timer.timeout.connect(self._send)
        QApplication.instance().installEventFilter(self)

    def activate(self):
        print("BINDING ACTIVE")
        self.timer.start(3000)

    def _send(self):
        print("Set Binding", self.current_binding)
        self.binding.emit(deepcopy(self.current_binding))
        self.current_binding = []
        self.timer.stop()

    def eventFilter(self, watched_obj, event):
        if not self.timer.isActive():
            return super().eventFilter(watched_obj, event)

        if event.type() == QEvent.Type.KeyPress:
            if event.isAutoRepeat():
                return True

            key = BindingCapture._get_event_key(event)
            self.current_binding.append(key)
            print("PRESSED", key)
            self.update.emit(self.current_binding)

            return True

        return super().eventFilter(watched_obj, event)

    @staticmethod
    def _get_event_key(event: QEvent) -> str:
        assert event.type() == QEvent.Type.KeyPress
        key_text = event.text()
        if not key_text or key_text.isspace():
            return Qt.Key(event.key()).name
        else:
            return key_text