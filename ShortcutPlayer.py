from components.bindings import BindingManager
from CameraAI.ai_vision import VisionManager, Frame, Annotated
from pynput.keyboard import Controller, Key
from PyQt6.QtCore import QObject


KEY_MAP = {
    # Media keys (correct names)
    "Key_VolumeMute": Key.media_volume_mute,
    "Key_VolumeDown": Key.media_volume_down,
    "Key_VolumeUp": Key.media_volume_up,
    "Key_PlayPause": Key.media_play_pause,
    "Key_Next": Key.media_next,
    "Key_Prev": Key.media_previous,

    # Modifier keys
    "Key_Ctrl": Key.ctrl,
    "Key_Alt": Key.alt,
    "Key_Shift": Key.shift,
    "Key_Cmd": Key.cmd,

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

class Shortcuter(QObject):
    def __init__(self, binding_manager: BindingManager):
        super().__init__()
        self.keyboard = Controller()
        self.binding_manager = binding_manager
        self.vision_manager = VisionManager.instance()
        self.vision_manager.annotated_frame_ready.connect(self._frame)
        self.binding_manager = binding_manager
        self.keyboard = Controller()

        self.previous_gesture_name = None

    def _frame(self, t: Annotated):
        frame, landmarkers = t.get()
        if landmarkers is None or not landmarkers.hand_landmarks:
            self.previous_gesture_name = None  # reset when hand leaves frame
            return False

        name, confidence = self.vision_manager.recognise_gesture(self.binding_manager.bindings, landmarkers.hand_landmarks)

        if not self.binding_manager.bindings or name is None or name == self.previous_gesture_name:
            self.previous_gesture_name = name
            return False

        binding = self.binding_manager.bindings[name]

        self.previous_gesture_name = name
        print(f"Name: {name}, Confidence: {confidence}")
        self._process(binding.shortcut)
        return True


    def _process(self, shortcut: list[str]):
        for k in shortcut:
            if len(k) == 1:
                self.keyboard.tap(k)
            else:
                # Check mapping first
                if k in KEY_MAP:
                    special = KEY_MAP[k]
                else:
                    # Try direct conversion
                    special = getattr(Key, k.lower().replace("key_", ""), None)

                if special:
                    self.keyboard.tap(special)
                    print(f"Playing key: {special}")
                else:
                    print(f"Unknown key: {k}")