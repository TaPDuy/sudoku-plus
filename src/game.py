import pygame as pg
from pygame.rect import Rect, RectType
from pygame.sprite import LayeredDirty

from .app import Application
from .application import ActionManager, BoardInputAction
from .sudoku.board import Board


class Game(Application):

    def __init__(self):
        super().__init__()

        self.action_manager = ActionManager()

        self.sprites = LayeredDirty()

        self.board = Board(self.sprites)

    def _process_events(self):
        for evt in pg.event.get():
            match evt.type:
                case pg.WINDOWCLOSE:
                    self.close()
                case pg.KEYDOWN:
                    match evt.key:
                        case pg.K_ESCAPE:
                            self.close()
                        case pg.K_z:
                            if pg.key.get_mods() & pg.KMOD_CTRL:
                                self.action_manager.undo()
                        case pg.K_y:
                            if pg.key.get_mods() & pg.KMOD_CTRL:
                                self.action_manager.redo()
                        case pg.K_1 | pg.K_2 | pg.K_3 | pg.K_4 | pg.K_5 | pg.K_6 | pg.K_7 | pg.K_8 | pg.K_9:
                            old_values = self.board.fill_tiles(evt.key - pg.K_0, Board.INPUT_MODE_VALUE)
                            self.action_manager.new_action(BoardInputAction(
                                self.board,
                                evt.key - pg.K_0,
                                Board.INPUT_MODE_VALUE,
                                old_values
                            ))
                        case pg.K_KP1 | pg.K_KP2 | pg.K_KP3 | pg.K_KP4 | pg.K_KP5 | pg.K_KP6 | pg.K_KP7 | pg.K_KP8 | pg.K_KP9:
                            old_values = self.board.fill_tiles(evt.key - pg.K_KP1 + 1, Board.INPUT_MODE_COLOR)
                            self.action_manager.new_action(BoardInputAction(
                                self.board,
                                evt.key - pg.K_KP1 + 1,
                                Board.INPUT_MODE_COLOR,
                                old_values
                            ))
                case pg.MOUSEBUTTONDOWN:
                    self.board.mouse_button_down()
                case pg.MOUSEBUTTONUP:
                    self.board.mouse_button_up()

    def _update(self, dt):
        self.sprites.update()

    def _draw(self, surface) -> list[Rect | RectType]:
        return self.sprites.draw(surface)
