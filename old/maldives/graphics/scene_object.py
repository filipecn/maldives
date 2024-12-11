from abc import ABC, abstractmethod


class SceneObject(ABC):
    want_use_mouse: bool

    def __init__(self):
        self.want_use_mouse = False

    @abstractmethod
    def draw(self, camera):
        pass

    @abstractmethod
    def draw_gui(self, camera):
        pass

    @abstractmethod
    def mouse_drag_event(self, dx, dy):
        pass

    @abstractmethod
    def mouse_scroll_event(self, x_offset, y_offset):
        pass

    @abstractmethod
    def mouse_press_event(self, x, y, button):
        pass

    @abstractmethod
    def mouse_release_event(self, x: int, y: int, button: int):
        pass
