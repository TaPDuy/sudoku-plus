import pygame as pg
import pygame_gui as pgui
from pygame.rect import Rect, RectType
from pygame.sprite import LayeredDirty

from .app import Application
from .core import ActionManager, BoardInputAction
from .sudoku.board import Board, InputMode
from .sudoku.input import InputPanel
from .sudoku.rules import \
    RuleManager, SudokuRule, \
    generate_killer_mesh, killer_sudoku, KillerRule, \
    arrow, ArrowRule, \
    thermometer, ThermometerRule, \
    PalindromeRule, palindrome

from functools import partial


class Game(Application):

    def __init__(self):
        super().__init__()
        self.sprites = LayeredDirty()

        self.action_manager = ActionManager()

        self.board = Board(self.sprites)

        self.rule_manager = RuleManager(self.board, [
            SudokuRule(),
            KillerRule(28, {(0, 1), (1, 0), (1, 1), (2, 1), (3, 1), (0, 2), (1, 2)}),
            ArrowRule((1, 1), [(2, 3), (2, 4), (1, 4)]),
            ThermometerRule([(7, 7), (7, 6), (6, 6), (5, 5), (5, 6), (4, 6), (4, 5), (5, 4)]),
            PalindromeRule([(0, 5), (1, 6), (2, 7), (3, 6), (4, 5), (5, 4)])
        ])
        generate_killer_mesh()
        killer_sudoku(self.board.image, KillerRule(28, {(0, 1), (1, 0), (1, 1), (2, 1), (3, 1), (0, 2), (1, 2)}))
        arrow(self.board.image, ArrowRule((1, 1), [(2, 3), (2, 4), (1, 4)]))
        thermometer(self.board.image, ThermometerRule([(7, 7), (7, 6), (6, 6), (5, 5), (5, 6), (4, 6), (4, 5), (5, 4)]))
        palindrome(self.board.image, PalindromeRule([(0, 5), (1, 6), (2, 7), (3, 6), (4, 5), (5, 4)]))
        self.board.dirty = 1

        self.input = InputPanel((500, 48), self.ui_manager)
        self.input.assign(0, partial(self.fill_selection, 1))
        self.input.assign(1, partial(self.fill_selection, 2))
        self.input.assign(2, partial(self.fill_selection, 3))
        self.input.assign(3, partial(self.fill_selection, 4))
        self.input.assign(4, partial(self.fill_selection, 5))
        self.input.assign(5, partial(self.fill_selection, 6))
        self.input.assign(6, partial(self.fill_selection, 7))
        self.input.assign(7, partial(self.fill_selection, 8))
        self.input.assign(8, partial(self.fill_selection, 9))
        self.input.assign(InputPanel.BUTTON_VALUE, partial(self.select_input_mode, InputPanel.BUTTON_VALUE))
        self.input.assign(InputPanel.BUTTON_MARK, partial(self.select_input_mode, InputPanel.BUTTON_MARK))
        self.input.assign(InputPanel.BUTTON_COLOR, partial(self.select_input_mode, InputPanel.BUTTON_COLOR))
        self.input.assign(InputPanel.BUTTON_UNDO, self.action_manager.undo)
        self.input.assign(InputPanel.BUTTON_REDO, self.action_manager.redo)
        self.input.assign(InputPanel.BUTTON_CHECK, self.check_win)

        # Event handlers
        self.board.on_changed.add_handler(self.rule_manager.update)

    def check_win(self):
        if self.rule_manager.check():
            print("You win!")
        else:
            print("Something's wrong...")

    def select_input_mode(self, index):
        self.input.toggle_highlight_button(self.input.force_mode.value + InputPanel.BUTTON_VALUE)
        self.input.toggle_highlight_button(index)
        self.input.force_mode = InputMode(index - InputPanel.BUTTON_VALUE)

    def fill_selection(self, value):
        mode = InputMode((pg.key.get_mods() & pg.KMOD_SHIFT) | (bool(pg.key.get_mods() & pg.KMOD_CTRL) << 1) or self.input.force_mode.value)
        mode = self.input.force_mode if mode == 3 else mode

        if mode == InputMode.INPUT_MODE_VALUE or value != 0:
            old_values = self.board.fill_tiles(value, mode)

            self.action_manager.new_action(BoardInputAction(
                self.board,
                value,
                mode,
                old_values
            ))

    def _process_events(self, evt):
        match evt.type:
            case pg.WINDOWCLOSE:
                self.close()
            case pg.KEYDOWN:
                match evt.key:
                    case pg.K_ESCAPE:
                        self.close()
                    case pg.K_z:
                        if evt.mod & pg.KMOD_CTRL:
                            self.action_manager.undo()
                    case pg.K_y:
                        if evt.mod & pg.KMOD_CTRL:
                            self.action_manager.redo()
                    case pg.K_BACKSPACE:
                        self.fill_selection(0)
                    case pg.K_1 | pg.K_2 | pg.K_3 | pg.K_4 | pg.K_5 | pg.K_6 | pg.K_7 | pg.K_8 | pg.K_9:
                        self.input.toggle_highlight_button(evt.key - pg.K_1)
                        self.input.trigger_button(evt.key - pg.K_1)
                    case pg.K_KP1 | pg.K_KP2 | pg.K_KP3 | pg.K_KP4 | pg.K_KP5 | pg.K_KP6 | pg.K_KP7 | pg.K_KP8 | pg.K_KP9:
                        self.input.toggle_highlight_button(evt.key - pg.K_KP1)
                        self.input.trigger_button(evt.key - pg.K_KP1)
            case pg.KEYUP:
                match evt.key:
                    case pg.K_1 | pg.K_2 | pg.K_3 | pg.K_4 | pg.K_5 | pg.K_6 | pg.K_7 | pg.K_8 | pg.K_9:
                        self.input.toggle_highlight_button(evt.key - pg.K_1)
                    case pg.K_KP1 | pg.K_KP2 | pg.K_KP3 | pg.K_KP4 | pg.K_KP5 | pg.K_KP6 | pg.K_KP7 | pg.K_KP8 | pg.K_KP9:
                        self.input.toggle_highlight_button(evt.key - pg.K_KP1)
            case pg.MOUSEBUTTONDOWN:
                self.board.mouse_button_down()
            case pg.MOUSEBUTTONUP:
                self.board.mouse_button_up()
            case pgui.UI_BUTTON_PRESSED:
                self.input.button_pressed(evt)

    def _update(self, dt):
        self.sprites.update()

    def _draw(self, surface) -> list[Rect | RectType]:
        return self.sprites.draw(surface)
