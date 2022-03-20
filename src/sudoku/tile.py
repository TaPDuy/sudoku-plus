from pygame import Surface, SRCALPHA
from pygame.font import SysFont

from ..gfx import Graphics


class Tile:
    SIZE = 64

    def __init__(self, pxpos: tuple[float, float]):
        self.pxpos = self.pxx, self.pxy = pxpos
        self.pxsize = self.pxw, self.pxh = Tile.SIZE, Tile.SIZE

        self.value = 0
        self.mark = 0
        self.color = 0

        # Graphics properties
        self.__surface = Surface(self.pxsize, SRCALPHA)
        self.__font_value = SysFont("Arial", 48)
        self.__font_mark = SysFont("Arial", 14)
        self.__redraw()

    def set_value(self, value: int):
        self.value = value

    def mark(self, value: int):
        self.mark ^= 1 << (value - 1)

    def set_color(self, index: int):
        self.color = index

    def update(self):
        pass

    def draw(self, surface: Surface, blend_mode=0):
        surface.blit(self.__surface, self.pxpos, special_flags=blend_mode)

    def __redraw(self):
        # Map color later
        if self.color:
            Graphics.rect(self.__surface, (0, 0), self.pxsize, (0, 0, 255))

        if 0 < self.value < 10:
            text = self.__font_value.render(str(self.value), True, (255, 255, 255))
            self.__surface.blit(text, (
                self.pxw / 2 - text.get_width() / 2,
                self.pxh / 2 - text.get_height() / 2
            ))
        elif self.mark:
            textstr = ''.join(str(i + 1) for i in range(9) if 1 << i & self.mark)
            text = self.__font_mark.render(textstr, True, (255, 255, 255))
            self.__surface.blit(text, (
                self.pxw / 2 - text.get_width() / 2,
                self.pxh / 2 - text.get_height() / 2
            ))
