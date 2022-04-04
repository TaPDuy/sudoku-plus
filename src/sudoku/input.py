from pygame.rect import Rect
from pygame_gui import UIManager
from pygame_gui.elements import UIButton

from .board import InputMode


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

        self.force_mode = InputMode.INPUT_MODE_VALUE
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

    def button_pressed(self, evt):
        for i in range(InputPanel.BUTTONS_NUM):
            if evt.ui_element == self.buttons[i]:
                self.trigger_button(i)
