from pygame import Rect
from pygame_gui.core.interfaces import IUIManagerInterface
from pygame_gui.elements import UIPanel, UIButton


class Menu(UIPanel):
    def __init__(self, pos: tuple[float, float], manager: IUIManagerInterface, container=None):
        super().__init__(Rect(pos, (300, 30)), 0, manager, container=container)
        self.save_btn = UIButton(Rect(0, 0, 100, 30), "Save", manager, self)
        self.open_btn = UIButton(Rect(100, 0, 100, 30), "Open", manager, self)
        self.new_btn = UIButton(Rect(200, 0, 100, 30), "New", manager, self)
