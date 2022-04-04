import pygame as pg
import pygame_gui as pgui
from pygame.rect import Rect, RectType
from pygame.sprite import LayeredDirty

from .app import Application
from .core import ActionManager
from .sudoku.board import Board
from .sudoku.input import InputPanel
from .sudoku.rule import RuleManager, SudokuRule, KillerRule


class Game(Application):

    def __init__(self):
        super().__init__()
        self.sprites = LayeredDirty()

        self.action_manager = ActionManager()

        self.board = Board(self.sprites)
        self.rule_manager = RuleManager(self.board, [
            SudokuRule(),
            KillerRule(19, [(0, 0), (1, 0), (2, 0), (3, 0), (3, 1)])
        ])
        self.input = InputPanel((500, 48), self.ui_manager, self.board, self.action_manager, self.rule_manager)

        # Event handlers
        self.board.on_changed.add_handler(self.rule_manager.update)

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
