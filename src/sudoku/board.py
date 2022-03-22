from pygame import Surface, SRCALPHA
from pygame.sprite import DirtySprite, AbstractGroup
from pygame.rect import Rect

from ..gfx import Graphics
from .tile import Tile
from .selection import SelectionGrid


class Board(DirtySprite):

    def __init__(self, sprite_groups: AbstractGroup):
        super().__init__()

        # Data properties
        self.pxpos = self.pxx, self.pxy = 10, 10
        self.tlsize = self.tlw, self.tlh = 9, 9
        self.pxsize = self.pxw, self.pxh = Tile.SIZE * self.tlw, Tile.SIZE * self.tlh

        # Graphics properties
        self.image = Surface(self.pxsize, SRCALPHA)
        self.rect = Rect(self.pxpos, self.pxsize)

        # Children properties
        self.__tiles = [
            [
                Tile((self.pxx + x * Tile.SIZE, self.pxy + y * Tile.SIZE), sprite_groups) for x in range(self.tlw)
            ] for y in range(self.tlh)
        ]

        # self.__surface = Surface(self.pxsize, SRCALPHA)
        sprite_groups.add(self)

        self.selection = SelectionGrid(self.pxpos, self.tlsize, sprite_groups)
        self.selection.select((2, 2))
        self.selection.select((3, 3))
        self.selection.select((1, 3))
        self.selection.select((2, 4))

        self.__initdraw()

    def update(self):
        pass

    # def draw(self, surface: Surface) -> list[Rect | RectType]:
    #     """Draw the board and childen components' surfaces on another surface."""
    #     # surface.blit(self.__surface, self.pxpos)
    #     return self.sprites.draw(surface)

    def __initdraw(self):
        """Draw initial sprite"""
        # for r in self.__tiles:
        #     for tl in r:
        #         tl.draw(self.image)

        for tly in range(self.tlh):
            Graphics.line(
                self.image,
                (0, tly * Tile.SIZE),
                (self.pxw, tly * Tile.SIZE),
                1 if tly % 3 else 2
            )

        for tlx in range(self.tlw):
            Graphics.line(
                self.image,
                (tlx * Tile.SIZE, 0),
                (tlx * Tile.SIZE, self.pxh),
                1 if tlx % 3 else 2
            )

        Graphics.line(self.image, (0, self.pxh - 1), (self.pxw, self.pxh - 1), 2)
        Graphics.line(self.image, (self.pxw - 1, 0), (self.pxw - 1, self.pxh), 2)
