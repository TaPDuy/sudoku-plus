import pygame
from pygame import Surface, SRCALPHA
from pygame.sprite import DirtySprite, AbstractGroup
from pygame.rect import Rect

from ..gfx import Graphics
from .tile import Tile
from .selection import SelectionGrid


def get_tile_pos(pxpos: tuple[float, float]) -> tuple[int, int]:
    return pxpos[0] // Tile.SIZE, pxpos[1] // Tile.SIZE


class Board(DirtySprite):
    INPUT_MODE_VALUE = 0
    INPUT_MODE_MARK = 1
    INPUT_MODE_COLOR = 2

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
        self.multi_select = False
        self.should_select = False

        self.__initdraw()

    def fill_tiles(self, value: int, mode: int):
        for x, y in self.selection.selected:
            match mode:
                case Board.INPUT_MODE_VALUE:
                    self.__tiles[y][x].set_value(value)
                case Board.INPUT_MODE_MARK:
                    self.__tiles[y][x].set_mark(value)
                case Board.INPUT_MODE_COLOR:
                    self.__tiles[y][x].set_color(value)

    def mouse_button_down(self):
        if not self.rect.collidepoint(pygame.mouse.get_pos()):
            return

        if not pygame.key.get_mods() & pygame.KMOD_SHIFT:
            self.selection.clear()

        self.multi_select = True
        self.should_select = not self.selection.is_selected(get_tile_pos(pygame.mouse.get_pos()))

    def mouse_button_up(self):
        self.multi_select = False

    def update(self):
        mpos = pygame.mouse.get_pos()
        if self.multi_select:
            if self.should_select:
                self.selection.select(get_tile_pos((mpos[0] - self.pxx, mpos[1] - self.pxy)))
            else:
                self.selection.unselect(get_tile_pos((mpos[0] - self.pxx, mpos[1] - self.pxy)))

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
