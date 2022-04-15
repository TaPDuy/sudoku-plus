import pygame as pg
import pygame_gui as pgui
from pygame.rect import Rect
from pygame_gui import UIManager
from pygame_gui.elements import UIButton


class InputPanel:
    BUTTON_SIZE = 48

    BUTTONS_NUM = 16

    BUTTON_VALUE = 9
    BUTTON_MARK = 10
    BUTTON_COLOR = 11

    BUTTON_UNDO = 12
    BUTTON_REDO = 13
    BUTTON_RESET = 14
    BUTTON_CHECK = 15

    def __init__(self, apos: tuple[float, float], manager: UIManager):
        self.apos = self.ax, self.ay = apos

        self.buttons = [UIButton(Rect(
            self.ax + x * InputPanel.BUTTON_SIZE,
            self.ay + (2 - y) * InputPanel.BUTTON_SIZE,
            InputPanel.BUTTON_SIZE,
            InputPanel.BUTTON_SIZE
        ), str(x + y * 3 + 1), manager) for y in range(3) for x in range(3)]

        self.buttons.append(UIButton(Rect(
            self.ax + 3 * InputPanel.BUTTON_SIZE,
            self.ay,
            InputPanel.BUTTON_SIZE,
            InputPanel.BUTTON_SIZE
        ), "value", manager))
        self.buttons.append(UIButton(Rect(
            self.ax + 3 * InputPanel.BUTTON_SIZE,
            self.ay + InputPanel.BUTTON_SIZE,
            InputPanel.BUTTON_SIZE,
            InputPanel.BUTTON_SIZE
        ), "mark", manager))
        self.buttons.append(UIButton(Rect(
            self.ax + 3 * InputPanel.BUTTON_SIZE,
            self.ay + 2 * InputPanel.BUTTON_SIZE,
            InputPanel.BUTTON_SIZE,
            InputPanel.BUTTON_SIZE
        ), "color", manager))

        self.buttons.append(UIButton(Rect(
            self.ax,
            self.ay + 3 * InputPanel.BUTTON_SIZE,
            InputPanel.BUTTON_SIZE,
            InputPanel.BUTTON_SIZE
        ), "undo", manager))
        self.buttons.append(UIButton(Rect(
            self.ax + InputPanel.BUTTON_SIZE,
            self.ay + 3 * InputPanel.BUTTON_SIZE,
            InputPanel.BUTTON_SIZE,
            InputPanel.BUTTON_SIZE
        ), "redo", manager))
        self.buttons.append(UIButton(Rect(
            self.ax + 2 * InputPanel.BUTTON_SIZE,
            self.ay + 3 * InputPanel.BUTTON_SIZE,
            InputPanel.BUTTON_SIZE,
            InputPanel.BUTTON_SIZE
        ), "reset", manager))
        self.buttons.append(UIButton(Rect(
            self.ax + 3 * InputPanel.BUTTON_SIZE,
            self.ay + 3 * InputPanel.BUTTON_SIZE,
            InputPanel.BUTTON_SIZE,
            InputPanel.BUTTON_SIZE
        ), "check", manager))

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
