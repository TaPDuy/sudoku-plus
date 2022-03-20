from pygame import Surface, SRCALPHA

from ..gfx import Graphics
from .tile import Tile


class Board:

    def __init__(self):
        # Data properties
        self.pxpos = self.pxx, self.pxy = 10, 10
        self.tlsize = self.tlw, self.tlh = 9, 9
        self.pxsize = self.pxw, self.pxh = Tile.SIZE * self.tlw, Tile.SIZE * self.tlh

        # Children properties
        self.__tiles = [
            [
                Tile((x * Tile.SIZE, y * Tile.SIZE)) for x in range(self.tlw)
            ] for y in range(self.tlh)
        ]

        # Graphics properties
        self.__surface = Surface(self.pxsize, SRCALPHA)
        self.__redraw()

    def update(self):
        pass

    def draw(self, surface: Surface):
        """Draw the board and childen components' surfaces on another surface."""
        surface.blit(self.__surface, self.pxpos)

    def __redraw(self):
        """Redraw the board's surface."""
        for r in self.__tiles:
            for tl in r:
                tl.draw(self.__surface)

        for tly in range(self.tlh):
            Graphics.line(
                self.__surface,
                (0, tly * Tile.SIZE),
                (self.pxw, tly * Tile.SIZE),
                1 if tly % 3 else 2
            )

        for tlx in range(self.tlw):
            Graphics.line(
                self.__surface,
                (tlx * Tile.SIZE, 0),
                (tlx * Tile.SIZE, self.pxh),
                1 if tlx % 3 else 2
            )

        Graphics.line(self.__surface, (0, self.pxh - 1), (self.pxw, self.pxh - 1), 2)
        Graphics.line(self.__surface, (self.pxw - 1, 0), (self.pxw - 1, self.pxh), 2)
