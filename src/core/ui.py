from pygame.rect import Rect
from pygame_gui.core.interfaces import IUIManagerInterface, IUIElementInterface
from pygame_gui.elements import UIPanel, UIButton
import pygame_gui as pgui
import pygame as pg

from core.event import Event


class ButtonGrid(UIPanel):

    class Button(UIButton):

        def __init__(
                self, rect: Rect, text: str, button_id: str,
                manager: IUIManagerInterface, container=None, sticky=False
        ):
            super().__init__(rect, text, manager, container)
            self.shadow_width = self.border_width = 0
            self.rebuild()

            self.id = button_id
            self.sticky = sticky
            self.highlight = False

        def set_highlight(self, b: bool):
            self.highlight = b
            if self.highlight:
                self.select()
            else:
                self.unselect()

    def __init__(
            self, grid_size: tuple[int, int], rect: Rect, padding: float,
            manager: IUIManagerInterface, container=None
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

        self.__keymap = {}
        self.__idmap = {}
        self.__buttons = []
        self.current_sticky = None

        self.on_button_pressed = Event()

    def process_event(self, evt):
        match evt.type:
            case pg.KEYDOWN:
                if evt.key in self.__keymap:
                    btn = self.__keymap.get(evt.key)
                    if not btn.highlight:
                        btn.set_highlight(True)
                        if btn.sticky:
                            self.current_sticky.set_highlight(False)
                            self.current_sticky = btn
            case pg.KEYUP:
                if evt.key in self.__keymap:
                    btn = self.__keymap.get(evt.key)
                    if not btn.sticky:
                        btn.set_highlight(False)
            case pgui.UI_BUTTON_PRESSED:
                if evt.ui_element in self.__buttons:
                    index = self.__buttons.index(evt.ui_element)

                    if self.__buttons[index].sticky:
                        self.current_sticky.set_highlight(False)
                        self.current_sticky = self.__buttons[index]
                        self.current_sticky.set_highlight(True)

                    self.on_button_pressed(button_id=self.__buttons[index].id)

    def add_button(self, text: str, button_id: str, sticky=False, keys: list = None):
        index = len(self.__buttons)
        x, y = index % self.grid_w, index // self.grid_w

        btn = ButtonGrid.Button(Rect((
            x * self.btn_w + (x + 1) * self.pad,
            y * self.btn_h + (y + 1) * self.pad
        ), self.btn_size), text, button_id, self.ui_manager, self, sticky)

        self.__buttons.append(btn)
        self.__idmap[button_id] = btn

        if keys:
            for key in keys:
                self.__keymap[key] = btn

        if sticky and not self.current_sticky:
            self.current_sticky = btn
            btn.set_highlight(True)

    def get_button(self, key: int | tuple[int, int] | str) -> IUIElementInterface | None:
        if type(key) is str:
            return self.__idmap.get(key)
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
