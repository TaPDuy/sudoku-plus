import pygame as pg
import pygame_gui as pgui
from pygame.rect import Rect
from pygame_gui.core.interfaces import IUIManagerInterface
from pygame_gui.elements import UIButton, UIPanel


class InputPanel(UIPanel):
    BUTTONS_NUM = 16

    BUTTON_VALUE = 9
    BUTTON_MARK = 10
    BUTTON_COLOR = 11

    BUTTON_UNDO = 12
    BUTTON_REDO = 13
    BUTTON_RESET = 14
    BUTTON_CHECK = 15

    def __init__(self, rect: Rect, gap: tuple[float, float], manager: IUIManagerInterface, container=None):
        super().__init__(
            rect, 0, manager, container=container,
            margins={'left': 0, 'right': 0, 'top': 0, 'bottom': 0}
        )

        self.gap = self.vgap, self.hgap = gap
        self.button_size = ((rect.w - 5 * self.hgap) / 4, (rect.h - 5 * self.vgap) / 4)

        self.buttons = [UIButton(Rect(
            (
                x * self.button_size[0] + (x + 1) * self.hgap,
                (2 - y) * self.button_size[1] + (3 - y) * self.vgap
            ), self.button_size
        ), str(x + y * 3 + 1), manager, self) for y in range(3) for x in range(3)]

        self.buttons.append(UIButton(Rect(
            (3 * self.button_size[0] + 4 * self.hgap, self.vgap),
            self.button_size
        ), "value", manager, self))
        self.buttons.append(UIButton(Rect(
            (3 * self.button_size[0] + 4 * self.hgap, self.button_size[1] + 2 * self.vgap),
            self.button_size
        ), "mark", manager, self))
        self.buttons.append(UIButton(Rect(
            (3 * self.button_size[0] + 4 * self.hgap, 2 * self.button_size[1] + 3 * self.vgap),
            self.button_size
        ), "color", manager, self))

        self.buttons.append(UIButton(Rect(
            (self.hgap, 3 * self.button_size[1] + 4 * self.vgap),
            self.button_size
        ), "undo", manager, self))
        self.buttons.append(UIButton(Rect(
            (self.button_size[0] + 2 * self.hgap, 3 * self.button_size[1] + 4 * self.vgap),
            self.button_size
        ), "redo", manager, self))
        self.buttons.append(UIButton(Rect(
            (2 * self.button_size[0] + 3 * self.hgap, 3 * self.button_size[1] + 4 * self.vgap),
            self.button_size
        ), "reset", manager, self))
        self.buttons.append(UIButton(Rect(
            (3 * self.button_size[0] + 4 * self.hgap, 3 * self.button_size[1] + 4 * self.vgap),
            self.button_size
        ), "check", manager, self))

        for btn in self.buttons:
            btn.shadow_width = 0
            btn.border_width = 0
            btn.rebuild()

        self.toggle_highlight_button(InputPanel.BUTTON_VALUE)
        self.functions = {}

    def assign(self, index: int, func):
        self.functions[index] = func

    def toggle_highlight_button(self, index: int):
        if self.buttons[index].is_selected:
            self.buttons[index].unselect()
        else:
            self.buttons[index].select()

    def trigger_button(self, index: int):
        if self.functions.get(index):
            self.functions[index]()

    def process_events(self, evt):
        match evt.type:
            case pg.KEYDOWN:
                match evt.key:
                    case pg.K_1 | pg.K_2 | pg.K_3 | pg.K_4 | pg.K_5 | pg.K_6 | pg.K_7 | pg.K_8 | pg.K_9:
                        self.toggle_highlight_button(evt.key - pg.K_1)
                    case pg.K_KP1 | pg.K_KP2 | pg.K_KP3 | pg.K_KP4 | pg.K_KP5 | pg.K_KP6 | pg.K_KP7 | pg.K_KP8 | pg.K_KP9:
                        self.toggle_highlight_button(evt.key - pg.K_KP1)
            case pg.KEYUP:
                match evt.key:
                    case pg.K_1 | pg.K_2 | pg.K_3 | pg.K_4 | pg.K_5 | pg.K_6 | pg.K_7 | pg.K_8 | pg.K_9:
                        self.toggle_highlight_button(evt.key - pg.K_1)
                    case pg.K_KP1 | pg.K_KP2 | pg.K_KP3 | pg.K_KP4 | pg.K_KP5 | pg.K_KP6 | pg.K_KP7 | pg.K_KP8 | pg.K_KP9:
                        self.toggle_highlight_button(evt.key - pg.K_KP1)
            case pgui.UI_BUTTON_PRESSED:
                for btn in self.buttons:
                    if evt.ui_element == btn:
                        self.trigger_button(self.buttons.index(btn))
