from enum import Enum

import pygame as pg
from pygame import Surface, SRCALPHA
from pygame.sprite import DirtySprite, LayeredDirty
from pygame.rect import Rect
from pygame_gui.core.interfaces import IUIManagerInterface

from core.gfx.graphics import Graphics
from .tile import Tile
from .selection import SelectionGrid
from core.action import new_action, Action
from core.event import Event, EventData


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

    def __init__(self, pxpos: tuple[float, float], pxsize: tuple[float, float], sprite_groups: LayeredDirty, manager: IUIManagerInterface):
        super().__init__()
        self.manager = manager

        # Data properties
        self.pxpos = self.pxx, self.pxy = pxpos
        self.tlsize = self.tlw, self.tlh = 9, 9
        self.pxsize = self.pxw, self.pxh = pxsize
        self.tile_size = self.pxw / self.tlw, self.pxh / self.tlh
        self.force_mode = InputMode.INPUT_MODE_VALUE

        # Graphics properties
        self.image = Surface(self.pxsize, SRCALPHA)
        self.rect = Rect(self.pxpos, self.pxsize)
        sprite_groups.add(self, layer=3)

        # Children properties
        self.__tiles = [[Tile(
            (self.pxx + x * self.tile_size[0], self.pxy + y * self.tile_size[1]),
            self.tile_size,
            sprite_groups
        ) for x in range(self.tlw)] for y in range(self.tlh)]
        self.old_conflicts = set()

        self.selection = SelectionGrid(self.pxpos, self.tlsize, self.tile_size, sprite_groups)
        self.multi_select = False
        self.should_select = False

        self.focusable: list[Rect] = [self.rect]
        self.is_focused = False

        # Events
        self.on_changed = Event()

        self.__initdraw()

    def get_tile_pos(self, pxpos: tuple[float, float]) -> tuple[int, int]:
        return int(pxpos[0] / self.tile_size[0]), int(pxpos[1] / self.tile_size[1])

    def get_numbered_tiles(self) -> dict[tuple[int, int], int]:
        return {(x, y): self.__tiles[y][x].value for y in range(self.tlh) for x in range(self.tlw) if self.__tiles[y][x].value}

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

    def fill_selection(self, value):
        mode = InputMode((pg.key.get_mods() & pg.KMOD_SHIFT) | (bool(pg.key.get_mods() & pg.KMOD_CTRL) << 1) or self.force_mode.value)
        mode = self.force_mode if mode == 3 else mode

        if mode == InputMode.INPUT_MODE_VALUE or value != 0:
            self.fill_tiles(value, mode)

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
            self.on_changed(EventData({'new_val': value, 'old_values': old_values}))

        return self, mode, old_values, value

    def set_focusable_areas(self, *rects):
        self.focusable = list(rects)

    def process_events(self, evt):
        match evt.type:
            case pg.MOUSEBUTTONDOWN:
                mouse_pos = pg.mouse.get_pos()
                self.is_focused = any(rect.collidepoint(*mouse_pos) for rect in self.focusable)

                if self.is_focused:
                    self.manager.set_focus_set(set())
                else:
                    self.selection.clear()

                if not self.rect.collidepoint(mouse_pos):
                    return
                if not pg.key.get_mods() & pg.KMOD_SHIFT:
                    self.selection.clear()

                self.multi_select = True
                self.should_select = not self.selection.is_selected(self.get_tile_pos(mouse_pos))
            case pg.MOUSEBUTTONUP:
                self.multi_select = False
            case pg.KEYDOWN:
                if not self.is_focused:
                    return
                match evt.key:
                    case pg.K_BACKSPACE:
                        self.fill_selection(0)
                    case pg.K_1 | pg.K_2 | pg.K_3 | pg.K_4 | pg.K_5 | pg.K_6 | pg.K_7 | pg.K_8 | pg.K_9:
                        self.fill_selection(evt.key - pg.K_1 + 1)
                    case pg.K_KP1 | pg.K_KP2 | pg.K_KP3 | pg.K_KP4 | pg.K_KP5 | pg.K_KP6 | pg.K_KP7 | pg.K_KP8 | pg.K_KP9:
                        self.fill_selection(evt.key - pg.K_KP1 + 1)

    def update(self):
        mpos = pg.mouse.get_pos()
        if self.multi_select and self.rect.collidepoint(pg.mouse.get_pos()):
            if self.should_select:
                self.selection.select(self.get_tile_pos((mpos[0] - self.pxx, mpos[1] - self.pxy)))
            else:
                self.selection.unselect(self.get_tile_pos((mpos[0] - self.pxx, mpos[1] - self.pxy)))

    def __initdraw(self):
        """Draw initial sprite"""
        # for r in self.__tiles:
        #     for tl in r:
        #         tl.draw(self.image)

        for tly in range(self.tlh):
            Graphics.line(
                self.image,
                (0, tly * self.tile_size[1]),
                (self.pxw, tly * self.tile_size[1]),
                1 if tly % 3 else 2,
                (140, 160, 160)
            )

        for tlx in range(self.tlw):
            Graphics.line(
                self.image,
                (tlx * self.tile_size[0], 0),
                (tlx * self.tile_size[0], self.pxh),
                1 if tlx % 3 else 2,
                (140, 160, 160)
            )

        Graphics.line(self.image, (0, self.pxh - 1), (self.pxw, self.pxh - 1), 2, (140, 160, 160))
        Graphics.line(self.image, (self.pxw - 1, 0), (self.pxw - 1, self.pxh), 2, (140, 160, 160))
