from pygame.rect import Rect
from pygame_gui.core.interfaces import IUIManagerInterface, IUIElementInterface
from pygame_gui.elements import UIPanel, UIButton


class ButtonGrid(UIPanel):

    def __init__(
            self,
            grid_size: tuple[int, int],
            rect: Rect,
            padding: float,
            manager: IUIManagerInterface,
            container=None
    ):
        super().__init__(
            rect, 0, manager, container=container,
            margins={'left': 0, 'right': 0, 'top': 0, 'bottom': 0}
        )

        self.pad = padding
        self.grid_size = self.grid_w, self.grid_h = grid_size
        self.btn_size = self.btn_w, self.btn_h = \
            (rect.w - (self.grid_w + 1) * self.pad) / self.grid_w, \
            (rect.h - (self.grid_h + 1) * self.pad) / self.grid_h

        self.__button_map = {}
        self.__buttons = []

    def add_button(self, text: str, button_id: str = None):
        index = len(self.__buttons)
        x, y = index % self.grid_w, index // self.grid_w

        btn = UIButton(Rect((
            x * self.btn_w + (x + 1) * self.pad,
            y * self.btn_h + (y + 1) * self.pad
        ), self.btn_size), text, self.ui_manager, self)

        self.__buttons.append(btn)
        if button_id:
            self.__button_map[button_id] = btn

    def get_button(self, key: int | tuple[int, int] | str) -> IUIElementInterface | None:
        if type(key) is str:
            return self.__button_map.get(key)
        elif type(key) is tuple:
            index = key[1] * self.grid_w + key[0]
            return self.__buttons[index] if index < len(self.__buttons) else None
        else:
            return self.__buttons[key] if key < len(self.__buttons) else None

    def set_grid_size(self, grid_size: tuple[int, int]):
        self.grid_size = self.grid_w, self.grid_h = grid_size
        self.btn_size = self.btn_w, self.btn_h = \
            (self.rect.w - (self.grid_w + 1) * self.pad) / self.grid_w, \
            (self.rect.h - (self.grid_h + 1) * self.pad) / self.grid_h

        for index, btn in enumerate(self.__buttons):
            x, y = index % self.grid_w, index // self.grid_w
            btn.set_relative_position((
                x * self.btn_w + (x + 1) * self.pad,
                y * self.btn_h + (y + 1) * self.pad
            ))
            btn.set_dimensions(self.btn_size)

    def set_relative_rect(self, rect: Rect):
        self.btn_size = self.btn_w, self.btn_h = \
            (rect.w - (self.grid_w + 1) * self.pad) / self.grid_w, \
            (rect.h - (self.grid_h + 1) * self.pad) / self.grid_h

        for index, btn in enumerate(self.__buttons):
            x, y = index % self.grid_w, index // self.grid_w
            btn.set_relative_position((
                x * self.btn_w + (x + 1) * self.pad,
                y * self.btn_h + (y + 1) * self.pad
            ))
            btn.set_dimensions(self.btn_size)

        self.set_relative_position(rect.topleft)
        self.set_dimensions(rect.size)


class TabController:

    def __init__(self):
        self.current_tab = 0
        self.__tabs: list[IUIElementInterface] = []

    def add_tab(self, tab: IUIElementInterface):
        self.__tabs.append(tab)
        if len(self.__tabs) - 1 != self.current_tab:
            tab.hide()

    def insert_tab(self, index: int, tab: IUIElementInterface):
        if index != self.current_tab:
            tab.hide()

        self.__tabs.insert(index, tab)
        if index <= self.current_tab:
            self.current_tab += 1

    def next_tab(self):
        self.set_tab((self.current_tab + 1) % len(self.__tabs))

    def prev_tab(self):
        self.set_tab((self.current_tab - 1) % len(self.__tabs))

    def set_tab(self, index: int):
        if index < 0 or index >= len(self.__tabs) or index == self.current_tab:
            return

        self.__tabs[self.current_tab].hide()
        self.__tabs[index].show()
        self.current_tab = index
