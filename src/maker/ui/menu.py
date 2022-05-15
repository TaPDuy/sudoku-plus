from pygame import Rect
from pygame_gui.core.interfaces import IUIManagerInterface
from pygame_gui.elements import UIPanel, UIButton


class Menu(UIPanel):
    def __init__(self, rect: Rect, manager: IUIManagerInterface, container=None, gap=5):
        super().__init__(
            rect, 0, manager, container=container,
            margins={'left': 0, 'right': 0, 'top': 0, 'bottom': 0}
        )

        self.gap = gap
        btnw, btnh = (rect.w - 4 * gap) / 3, rect.h - 2 * gap

        self.save_btn = UIButton(Rect(
            gap, gap, btnw, btnh
        ), "Save", manager, self)
        self.save_btn.shadow_width = 0
        self.save_btn.border_width = 0
        self.save_btn.rebuild()

        self.open_btn = UIButton(Rect(
            btnw + 2 * gap, gap, btnw, btnh
        ), "Open", manager, self)
        self.open_btn.shadow_width = 0
        self.open_btn.border_width = 0
        self.open_btn.rebuild()

        self.new_btn = UIButton(Rect(
            2 * btnw + 3 * gap, gap, btnw, btnh
        ), "New", manager, self)
        self.new_btn.shadow_width = 0
        self.new_btn.border_width = 0
        self.new_btn.rebuild()

    def set_relative_rect(self, rect: Rect):
        btnw, btnh = (rect.w - 4 * self.gap) / 3, rect.h - 2 * self.gap

        self.save_btn.set_relative_position((self.gap, self.gap))
        self.save_btn.set_dimensions((btnw, btnh))

        self.open_btn.set_relative_position((btnw + 2 * self.gap, self.gap))
        self.open_btn.set_dimensions((btnw, btnh))

        self.new_btn.set_relative_position((2 * btnw + 3 * self.gap, self.gap))
        self.new_btn.set_dimensions((btnw, btnh))

        self.set_relative_position(rect.topleft)
        self.set_dimensions(rect.size)
