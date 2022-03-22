import pygame as pg
from pygame.rect import Rect, RectType
from pygame.sprite import LayeredDirty

from .app import Application
from .sudoku.board import Board


class Game(Application):

    def __init__(self):
        super().__init__()

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

    def _update(self, dt):
        self.sprites.update()

    def _draw(self, surface) -> list[Rect | RectType]:
        return self.sprites.draw(surface)
