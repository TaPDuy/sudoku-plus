from pygame import Surface, SRCALPHA

from ..gfx import Graphics
from ..utils.constants import *


class Tile:
    SIZE = 64

    def __init__(self, pxpos: tuple[float, float]):
        self.pxpos = self.pxx, self.pxy = pxpos
        self.pxsize = self.pxw, self.pxh = Tile.SIZE, Tile.SIZE

        self.value = 0
        self.mark = [False] * 9
        self.color = 0

        # Graphics properties
        self.__surface = Surface(self.pxsize, SRCALPHA)
        self.__redraw()

    def update(self):
        pass

    def draw(self, surface: Surface, blend_mode=0):
        surface.blit(self.__surface, self.pxpos, special_flags=blend_mode)

    def __redraw(self):
        Graphics.pie(self.__surface, Tile.SIZE / 2, Tile.SIZE / 2, 10, 0, TWO_PI)
