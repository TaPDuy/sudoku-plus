from enum import Enum

import pygame as pg
from pygame import Surface, SRCALPHA
from pygame.sprite import DirtySprite, LayeredDirty
from pygame.rect import Rect

from src.core.gfx import Graphics
from .tile import Tile
from .selection import SelectionGrid
from ..core.event import Event
from src.core import new_action, Action


def get_tile_pos(pxpos: tuple[float, float]) -> tuple[int, int]:
    return pxpos[0] // Tile.SIZE, pxpos[1] // Tile.SIZE


class InputMode(Enum):
    INPUT_MODE_VALUE = 0
    INPUT_MODE_MARK = 1
    INPUT_MODE_COLOR = 2


class BoardInputAction(Action):

    def __init__(self, data):
        super().__init__(data)
        self.board = data[0]
        self.mode = data[1]
        self.old_values = data[2]
        self.value = data[3]

    def redo(self):
        self.board.fill_tiles(self.value, self.mode, self.old_values.keys(), no_record=True)

    def undo(self):
        for tile, val in self.old_values.items():
            self.board.fill_tiles(val, self.mode, {tile}, no_record=True)


class Board(DirtySprite):

    def __init__(self, sprite_groups: LayeredDirty):
        super().__init__()

        # Data properties
        self.pxpos = self.pxx, self.pxy = 32, 32
        self.tlsize = self.tlw, self.tlh = 9, 9
        self.pxsize = self.pxw, self.pxh = Tile.SIZE * self.tlw, Tile.SIZE * self.tlh

        # Graphics properties
        self.image = Surface(self.pxsize, SRCALPHA)
        self.rect = Rect(self.pxpos, self.pxsize)
        sprite_groups.add(self, layer=3)

        # Children properties
        self.__tiles = [
            [
                Tile((self.pxx + x * Tile.SIZE, self.pxy + y * Tile.SIZE), sprite_groups) for x in range(self.tlw)
            ] for y in range(self.tlh)
        ]
        self.old_conflicts = set()

        self.selection = SelectionGrid(self.pxpos, self.tlsize, sprite_groups)
        self.multi_select = False
        self.should_select = False

        # Events
        self.on_changed = Event()

        self.__initdraw()

    def is_complete(self) -> bool:
        for y in range(self.tlh):
            for x in range(self.tlw):
                if self.__tiles[y][x].value == 0:
                    return False
        return True

    def clear(self):
        for y in range(self.tlh):
            for x in range(self.tlw):
                self.__tiles[y][x].set_value(0).set_mark(0).set_color(0)
                self.__tiles[y][x].set_lock(False)

    def highlight_conflicts(self, conflicts: set):
        for cx, cy in self.old_conflicts.difference(conflicts):
            self.__tiles[cy][cx].set_highlight(False)
        for cx, cy in conflicts.difference(self.old_conflicts):
            self.__tiles[cy][cx].set_highlight(True)
        self.old_conflicts = conflicts

    def lock_tile(self, tiles: list[tuple[int, int]], lock: bool):
        for x, y in tiles:
            self.__tiles[y][x].set_lock(lock)

    @new_action(BoardInputAction)
    def fill_tiles(self, value: int, mode: InputMode, tiles=None):
        tiles = tiles or self.selection.selected

        old_values = {}
        for x, y in tiles:
            match mode:
                case InputMode.INPUT_MODE_VALUE:
                    if not self.__tiles[y][x].locked:
                        old_values[x, y] = self.__tiles[y][x].value
                        self.__tiles[y][x].set_value(value)
                case InputMode.INPUT_MODE_MARK:
                    old_values[x, y] = value
                    self.__tiles[y][x].set_mark(value)
                case InputMode.INPUT_MODE_COLOR:
                    old_values[x, y] = self.__tiles[y][x].color
                    self.__tiles[y][x].set_color(value)

        if mode == InputMode.INPUT_MODE_VALUE:
            self.on_changed(value, old_values)

        return self, mode, old_values, value

    def mouse_button_down(self):
        if not self.rect.collidepoint(pg.mouse.get_pos()):
            return

        if not pg.key.get_mods() & pg.KMOD_SHIFT:
            self.selection.clear()

        self.multi_select = True
        self.should_select = not self.selection.is_selected(get_tile_pos(pg.mouse.get_pos()))

    def mouse_button_up(self):
        self.multi_select = False

    def process_event(self, evt):
        match evt.type:
            case pg.MOUSEBUTTONDOWN:
                self.mouse_button_down()
            case pg.MOUSEBUTTONUP:
                self.mouse_button_up()

    def update(self):
        mpos = pg.mouse.get_pos()
        if self.multi_select and self.rect.collidepoint(pg.mouse.get_pos()):
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
                1 if tly % 3 else 2,
                (140, 160, 160)
            )

        for tlx in range(self.tlw):
            Graphics.line(
                self.image,
                (tlx * Tile.SIZE, 0),
                (tlx * Tile.SIZE, self.pxh),
                1 if tlx % 3 else 2,
                (140, 160, 160)
            )

        Graphics.line(self.image, (0, self.pxh - 1), (self.pxw, self.pxh - 1), 2, (140, 160, 160))
        Graphics.line(self.image, (self.pxw - 1, 0), (self.pxw - 1, self.pxh), 2, (140, 160, 160))
