from pygame.rect import Rect
from pygame_gui import UIManager
from pygame_gui.elements import UIButton
from pygame import KMOD_SHIFT, KMOD_CTRL
from pygame.key import get_mods

from .board import Board
from ..application.action import ActionManager, BoardInputAction
from ..utils.constants import InputMode


class InputPanel:
    BUTTON_SIZE = 48

    def __init__(self, apos: tuple[float, float], manager: UIManager, board: Board, action_manager: ActionManager):
        self.apos = self.ax, self.ay = apos

        self.board = board
        self.action_manager = action_manager

        self.force_mode = InputMode.INPUT_MODE_VALUE

        self.buttons = [UIButton(Rect(
            self.ax + x * InputPanel.BUTTON_SIZE,
            self.ay + (2 - y) * InputPanel.BUTTON_SIZE,
            InputPanel.BUTTON_SIZE,
            InputPanel.BUTTON_SIZE
        ), str(x + y * 3 + 1), manager) for y in range(3) for x in range(3)]

    def toggle_highlight_button(self, index: int):
        if self.buttons[index].is_selected:
            self.buttons[index].unselect()
        else:
            self.buttons[index].select()

    def trigger_button(self, index: int):
        mode = InputMode((get_mods() & KMOD_SHIFT) | (bool(get_mods() & KMOD_CTRL) << 1) or self.force_mode.value)
        old_values = self.board.fill_tiles(index + 1, mode)
        self.action_manager.new_action(BoardInputAction(
            self.board,
            index + 1,
            mode,
            old_values
        ))

    def button_pressed(self, evt):
        for i in range(9):
            if evt.ui_element == self.buttons[i]:
                self.trigger_button(i)
