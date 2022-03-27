from pygame import Surface, SRCALPHA
from pygame.font import SysFont
from pygame.sprite import DirtySprite, AbstractGroup
from pygame.rect import Rect

from ..gfx import Graphics


class Tile(DirtySprite):
    SIZE = 64

    def __init__(self, pxpos: tuple[float, float], sprite_groups: AbstractGroup):
        super().__init__(sprite_groups)

        # Graphics properties
        self.pxpos = self.pxx, self.pxy = pxpos
        self.pxsize = self.pxw, self.pxh = Tile.SIZE, Tile.SIZE
        self.image = Surface(self.pxsize, SRCALPHA)
        self.rect = Rect(self.pxpos, self.pxsize)

        self.value = 0
        self.mark = 0
        self.color = 0

        # self.__surface = Surface(self.pxsize, SRCALPHA)
        self.__font_value = SysFont("Arial", 48)
        self.__font_mark = SysFont("Arial", 14)
        self.__initdraw()

    def set_value(self, value: int):
        self.value = value
        self.dirty = 1
        self.__initdraw()

    def set_mark(self, value: int):
        self.mark ^= 1 << (value - 1)
        self.dirty = 1
        self.__initdraw()

    def set_color(self, index: int):
        self.color = index
        self.dirty = 1
        self.__initdraw()

    def update(self):
        pass

    # def draw(self, surface: Surface, blend_mode=0) -> list[Rect | RectType]:
    #     # surface.blit(self.__surface, self.pxpos, special_flags=blend_mode)
    #     return self.sprites.draw(surface)

    def __initdraw(self):
        self.image.fill((0, 0, 0, 0))

        # Map color later
        if self.color:
            Graphics.rect(self.image, (0, 0), self.pxsize, (0, 0, 255))

        if 0 < self.value < 10:
            text = self.__font_value.render(str(self.value), True, (255, 255, 255))
            self.image.blit(text, (
                self.pxw / 2 - text.get_width() / 2,
                self.pxh / 2 - text.get_height() / 2
            ))
        elif self.mark:
            textstr = ''.join(str(i + 1) for i in range(9) if 1 << i & self.mark)
            text = self.__font_mark.render(textstr, True, (255, 255, 255))
            self.image.blit(text, (
                self.pxw / 2 - text.get_width() / 2,
                self.pxh / 2 - text.get_height() / 2
            ))
