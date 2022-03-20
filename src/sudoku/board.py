from pygame import Surface
from ..gfx import Graphics


TILE_SIZE = 64


class Board:

    def __init__(self):
        # Data properties
        self.apos = self.ax, self.ay = 10, 10
        self.tlsize = self.tlw, self.tlh = 9, 9
        self.pxsize = self.pxw, self.pxh = TILE_SIZE * self.tlw, TILE_SIZE * self.tlh

        # Graphics properties
        self.__surface = Surface(self.pxsize)
        self.__redraw()

    def update(self):
        pass

    def draw(self, surface: Surface):
        """Draw the board's surface on a surface."""
        surface.blit(self.__surface, self.apos)

    def __redraw(self):
        """Redraw the board's surface."""
        for tly in range(self.tlh):
            Graphics.line(
                self.__surface,
                (0, tly * TILE_SIZE),
                (self.pxw, tly * TILE_SIZE),
                1 if tly % 3 else 2
            )

        for tlx in range(self.tlw):
            Graphics.line(
                self.__surface,
                (tlx * TILE_SIZE, 0),
                (tlx * TILE_SIZE, self.pxh),
                1 if tlx % 3 else 2
            )

        Graphics.line(self.__surface, (0, self.pxh - 1), (self.pxw, self.pxh - 1), 2)
        Graphics.line(self.__surface, (self.pxw - 1, 0), (self.pxw - 1, self.pxh), 2)
