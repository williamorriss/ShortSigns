import numpy as np

class BuildGestureEntry:
    def __init__(
            self,
            name: str | None = None,
            gesture: np.ndarray | None = None,
            shortcut: list[str] | None = None,
    ):
        self.name = name
        self.gesture = gesture
        self.shortcut = shortcut

    def set_name(self, name: str) -> "BuildGestureEntry":
        print("Set Name", name)
        self.name = name
        return self

    def set_gesture(self, gesture: np.ndarray) -> "BuildGestureEntry":
        print("Set Gesture", gesture)
        self.gesture = gesture
        return self

    def set_shortcut(self, shortcut: list[str]) -> "BuildGestureEntry":
        print("Set Shortcut", shortcut)
        self.shortcut = shortcut
        return self

    def all_set(self) -> bool:
        return (
                self.name is not None and
                self.gesture is not None and
                self.shortcut is not None

        )

    def reset(self):
        self.name = None
        self.gesture = None
        self.shortcut = None