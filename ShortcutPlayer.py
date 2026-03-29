from components.bindings import BindingManager
from CameraAI.ai_vision import VisionManager

from pynput.keyboard import Controller, Key

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QWidget

class ShortcutPlayer(QWidget):
    KEY_MAP = {
            # Media keys (correct names)
            "Key_VolumeMute": Key.media_volume_mute,
            "Key_VolumeDown": Key.media_volume_down,
            "Key_VolumeUp": Key.media_volume_up,
            "Key_PlayPause": Key.media_play_pause,
            "Key_Next": Key.media_next,
            "Key_Prev": Key.media_previous,
            "Key_Stop": Key.media_stop,
            
            # Modifier keys
            "Key_Ctrl": Key.ctrl,
            "Key_Alt": Key.alt,
            "Key_Shift": Key.shift,
            "Key_Meta": Key.cmd,
            
            # Navigation keys
            "Key_Space": Key.space,
            "Key_Enter": Key.enter,
            "Key_Tab": Key.tab,
            "Key_Esc": Key.esc,
            "Key_Backspace": Key.backspace,
            "Key_Delete": Key.delete,
            "Key_Home": Key.home,
            "Key_End": Key.end,
            "Key_PageUp": Key.page_up,
            "Key_PageDown": Key.page_down,
            
            # Arrow keys
            "Key_Up": Key.up,
            "Key_Down": Key.down,
            "Key_Left": Key.left,
            "Key_Right": Key.right,
        }

    def __init__(self, binding_manager: BindingManager):
        super().__init__()

        self.hide()

        self.timer = QTimer()
        self.timer.timeout.connect(self.regonise_play_shortcut)
        self.timer.start(10)

        self.keyboard = Controller()
        self.binding_manager = binding_manager
        self.vision_manager = VisionManager.instance()

        self.previous_gesture_name = None

    def regonise_play_shortcut(self) -> bool:
        frame = self.vision_manager.get_frame()
        landmarkers = self.vision_manager.get_landmarkers(frame)
        if landmarkers is None:
            return False

        name, confidence = self.vision_manager.recognise_gesture(self.binding_manager.bindings, landmarkers.hand_landmarks)

        if not self.binding_manager.bindings or name is None or name == self.previous_gesture_name:
            self.previous_gesture_name = name
            return False

        binding = self.binding_manager.bindings[name]
        shortcut = binding.shortcut

        print(f"Name: {name}, Confidence: {confidence}")
        self._play_shortcut(shortcut)
        
        self.previous_gesture_name = name

        return True

    def _play_shortcut(self, shortcut: list[str]):
        presses = []
        for k in shortcut:
            if len(k) == 1:
                self.keyboard.press(k)
                presses.append(k)
            else:
                # Check mapping first
                if k in self.KEY_MAP:
                    special = self.KEY_MAP[k]
                else:
                    # Try direct conversion
                    special = getattr(Key, k.lower().replace("key_", ""), None)
                
                if special:
                    print(f"Playing key: {special}")
                    self.keyboard.press(special)
                    presses.append(special)
                else:
                    print(f"Unknown key: {k}")

        for k in presses:
            self.keyboard.release(k)