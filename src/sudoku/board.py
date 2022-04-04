from enum import Enum

import pygame
from pygame import Surface, SRCALPHA
from pygame.sprite import DirtySprite, AbstractGroup
from pygame.rect import Rect

from src.core.gfx import Graphics
from .tile import Tile
from .selection import SelectionGrid
from ..core.event import Event


def get_tile_pos(pxpos: tuple[float, float]) -> tuple[int, int]:
    return pxpos[0] // Tile.SIZE, pxpos[1] // Tile.SIZE


class InputMode(Enum):
    INPUT_MODE_VALUE = 0
    INPUT_MODE_MARK = 1
    INPUT_MODE_COLOR = 2


class Board(DirtySprite):

    def __init__(self, sprite_groups: AbstractGroup):
        super().__init__()

        # Data properties
        self.pxpos = self.pxx, self.pxy = 32, 32
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
        self.old_conflicts = set()
        # self.__surface = Surface(self.pxsize, SRCALPHA)
        sprite_groups.add(self)

        self.selection = SelectionGrid(self.pxpos, self.tlsize, sprite_groups)
        self.multi_select = False
        self.should_select = False

        # Events
        self.on_changed = Event()

        self.__initdraw()

    def highlight_conflicts(self, conflicts: set):
        for cx, cy in self.old_conflicts.difference(conflicts):
            self.__tiles[cy][cx].set_highlight(False)
        for cx, cy in conflicts.difference(self.old_conflicts):
            self.__tiles[cy][cx].set_highlight(True)
        self.old_conflicts = conflicts

    def __set_value(self, x, y, value) -> int:
        if self.__tiles[y][x].value == value:
            value = 0
        return self.__tiles[y][x].set_value(value)

    def fill_tiles(self, value: int, mode: InputMode, tiles=None) -> dict[tuple[int, int], int]:
        tiles = tiles or self.selection.selected

        old_values = {}
        for x, y in tiles:
            match mode:
                case InputMode.INPUT_MODE_VALUE:
                    old_values[x, y] = self.__set_value(x, y, value)
                case InputMode.INPUT_MODE_MARK:
                    old_values[x, y] = self.__tiles[y][x].set_mark(value)
                case InputMode.INPUT_MODE_COLOR:
                    old_values[x, y] = self.__tiles[y][x].set_color(value)

        if mode == InputMode.INPUT_MODE_VALUE:
            self.on_changed(value, old_values)

        return old_values

    def fill_tile(self, value: int, mode: InputMode, tlpos: tuple[int, int]) -> int:
        old_value = 0
        match mode:
            case InputMode.INPUT_MODE_VALUE:
                old_value = self.__set_value(tlpos[0], tlpos[1], value)
            case InputMode.INPUT_MODE_MARK:
                old_value = self.__tiles[tlpos[1]][tlpos[0]].set_mark(value)
            case InputMode.INPUT_MODE_COLOR:
                old_value = self.__tiles[tlpos[1]][tlpos[0]].set_color(value)

        if mode == InputMode.INPUT_MODE_VALUE:
            self.on_changed(value, {tlpos: old_value})

        return old_value

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
        if self.multi_select and self.rect.collidepoint(pygame.mouse.get_pos()):
            if self.should_select:
                self.selection.select(get_tile_pos((mpos[0] - self.pxx, mpos[1] - self.pxy)))
            else:
                self.selection.unselect(get_tile_pos((mpos[0] - self.pxx, mpos[1] - self.pxy)))

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
