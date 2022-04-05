from pygame import Surface, SRCALPHA
from pygame.sprite import DirtySprite, AbstractGroup
from pygame.rect import Rect

import numpy as np

from src.core.gfx.graphics import Graphics
from src.core.utils.constants import *
from .tile import Tile

from functools import cache


class SelectionGrid:
    sprite_map = {}

    def __init__(
            self,
            apos: tuple[float, float],
            tlsize: tuple[int, int],
            sprite_groups: AbstractGroup
    ):
        self.apos = self.ax, self.ay = apos
        self.tlsize = self.tlw, self.tlh = tlsize
        self.selected = set()

        # self.mesh = MeshGrid(
        #     (self.ax - Tile.SIZE / 2, self.ay - Tile.SIZE / 2),
        #     (tlsize[0] * 2 + 3, tlsize[1] * 2 + 3),
        #     Tile.SIZE / 2,
        #     sprite_groups
        # )

        # Sprites
        self.spr_size = self.spr_w, self.spr_h = (Tile.SIZE / 2, Tile.SIZE / 2)
        self.spr_grid_size = self.spr_grid_w, self.spr_grid_h = (self.tlw + 1) << 1, (self.tlh + 1) << 1
        self.spr_grid_apos = self.spr_grid_ax, self.spr_grid_ay = self.ax - self.spr_w, self.ay - self.spr_h
        self.spr_grid = [[SelectionTile(
            (self.spr_grid_ax + x * self.spr_w, self.spr_grid_ay + y * self.spr_h),
            self.spr_size,
            sprite_groups
        ) for x in range(self.spr_grid_w)] for y in range(self.spr_grid_h)]

        self.generate_mesh_sprites(.25, (255, 0, 255, 150), 1, (255, 0, 255))
        self.mesh_grid = MeshGrid(
            self.spr_grid_size,
            (self.spr_grid_w + 1, self.spr_grid_h + 1)
        )

    def clear(self):
        self.selected.clear()
        self.mesh_grid.reset()
        for _ in self.spr_grid:
            for tile in _:
                tile.redraw(0)

    def is_selected(self, tlpos: tuple[int, int]) -> bool:
        return tlpos in self.selected

    def select(self, tlpos: tuple[int, int]):
        if tlpos in self.selected:
            return

        mtlx, mtly = (tlpos[0] << 1) + 1, (tlpos[1] << 1) + 1
        affected = self.mesh_grid.add(
            1,
            {(mtlx + dx, mtly + dy) for dx in range(3) for dy in range(3)}
        )

        for x, y in affected:
            self.spr_grid[y][x].redraw(self.mesh_grid.states[y][x])

        self.selected.add(tlpos)

    def unselect(self, tlpos: tuple[int, int]):
        if tlpos not in self.selected:
            return

        mtlx, mtly = (tlpos[0] << 1) + 1, (tlpos[1] << 1) + 1
        affected = self.mesh_grid.add(
            -1,
            {(mtlx + dx, mtly + dy) for dx in range(3) for dy in range(3)}
        )

        for x, y in affected:
            self.spr_grid[y][x].redraw(self.mesh_grid.states[y][x])

        self.selected.remove(tlpos)

    def generate_mesh_sprites(
        self,
        extrude_weight: float = 0.25,
        color=(255, 255, 255),
        stroke_weight: float = 1,
        stroke_color=(255, 255, 255)
    ):
        w = np.clip(extrude_weight, 0.0, 0.99)
        cw = 1 - w

        if w == 0:
            stroke_weight = 0

        self.sprite_map[0] = Surface(self.spr_size, SRCALPHA)

        surface = Surface(self.spr_size, SRCALPHA)
        Graphics.pie(
            surface,
            0, 0,
            self.spr_w * w,
            -HALF_PI, 0,
            color, stroke_weight, stroke_color
        )
        self.sprite_map[1] = surface

        surface = Surface(self.spr_size, SRCALPHA)
        Graphics.pie(
            surface,
            self.spr_w, 0,
            self.spr_w * w,
            PI, PI * 1.5,
            color, stroke_weight, stroke_color
        )
        self.sprite_map[2] = surface

        surface = Surface(self.spr_size, SRCALPHA)
        Graphics.rect(
            surface,
            (0, 0),
            (self.spr_w, self.spr_w * w),
            color
        )
        Graphics.line(
            surface,
            (0, self.spr_w * w),
            (self.spr_w, self.spr_w * w),
            stroke_weight, stroke_color
        )
        self.sprite_map[3] = surface

        surface = Surface(self.spr_size, SRCALPHA)
        Graphics.pie(
            surface,
            self.spr_w, self.spr_w,
            self.spr_w * w,
            HALF_PI, PI,
            color, stroke_weight, stroke_color
        )
        self.sprite_map[4] = surface

        surface = Surface(self.spr_size, SRCALPHA)
        Graphics.pie(
            surface,
            0, 0,
            self.spr_w * w,
            -HALF_PI, 0,
            color, stroke_weight, stroke_color
        )
        Graphics.pie(
            surface,
            self.spr_w, self.spr_w,
            self.spr_w * w,
            HALF_PI, PI,
            color, stroke_weight, stroke_color
        )
        self.sprite_map[5] = surface

        surface = Surface(self.spr_size, SRCALPHA)
        Graphics.rect(
            surface,
            (self.spr_w * cw, 0),
            (self.spr_w * w, self.spr_w),
            color
        )
        Graphics.line(
            surface,
            (self.spr_w * cw, 0),
            (self.spr_w * cw, self.spr_w),
            stroke_weight, stroke_color
        )
        self.sprite_map[6] = surface

        surface = Surface(self.spr_size, SRCALPHA)
        Graphics.inverse_pie(
            surface,
            0, self.spr_w,
            self.spr_w * cw, self.spr_w,
            0, HALF_PI,
            color, stroke_weight, stroke_color
        )
        self.sprite_map[7] = surface

        surface = Surface(self.spr_size, SRCALPHA)
        Graphics.pie(
            surface,
            0, self.spr_w,
            self.spr_w * w,
            0, HALF_PI,
            color, stroke_weight, stroke_color
        )
        self.sprite_map[8] = surface

        surface = Surface(self.spr_size, SRCALPHA)
        Graphics.rect(
            surface,
            (0, 0),
            (self.spr_w * w, self.spr_w),
            color
        )
        Graphics.line(
            surface,
            (self.spr_w * w, 0),
            (self.spr_w * w, self.spr_w),
            stroke_weight, stroke_color
        )
        self.sprite_map[9] = surface

        surface = Surface(self.spr_size, SRCALPHA)
        Graphics.pie(
            surface,
            self.spr_w, 0,
            self.spr_w * w,
            PI, PI * 1.5,
            color, stroke_weight, stroke_color
        )
        Graphics.pie(
            surface,
            0, self.spr_w,
            self.spr_w * w,
            0, HALF_PI,
            color, stroke_weight, stroke_color
        )
        self.sprite_map[10] = surface

        surface = Surface(self.spr_size, SRCALPHA)
        Graphics.inverse_pie(
            surface,
            self.spr_w, self.spr_w,
            self.spr_w * cw, self.spr_w,
            HALF_PI, PI,
            color, stroke_weight, stroke_color
        )
        self.sprite_map[11] = surface

        surface = Surface(self.spr_size, SRCALPHA)
        Graphics.rect(
            surface,
            (0, self.spr_w * cw),
            (self.spr_w, self.spr_w * w),
            color
        )
        Graphics.line(
            surface,
            (0, self.spr_w * cw),
            (self.spr_w, self.spr_w * cw),
            stroke_weight, stroke_color
        )
        self.sprite_map[12] = surface

        surface = Surface(self.spr_size, SRCALPHA)
        Graphics.inverse_pie(
            surface,
            self.spr_w, 0,
            self.spr_w * cw, self.spr_w,
            -PI, -HALF_PI,
            color, stroke_weight, stroke_color
        )
        self.sprite_map[13] = surface

        surface = Surface(self.spr_size, SRCALPHA)
        Graphics.inverse_pie(
            surface,
            0, 0,
            self.spr_w * cw, self.spr_w,
            -HALF_PI, 0,
            color, stroke_weight, stroke_color
        )
        self.sprite_map[14] = surface

        surface = Surface(self.spr_size, SRCALPHA)
        Graphics.rect(
            surface,
            (0, 0),
            (self.spr_w, self.spr_w),
            color
        )
        self.sprite_map[15] = surface


# class MeshGrid:
#     state_sprite_map = {}
#
#     def __init__(
#             self,
#             apos: tuple[float, float],
#             tlsize: tuple[int, int],
#             tile_size,
#             sprite_groups: AbstractGroup
#     ):
#         self.apos = self.ax, self.ay = apos
#         self.tile_size = tile_size
#         self.sfsize = self.sfw, self.sfh = tlsize[0] + 1, tlsize[1] + 1
#         self.scalar_field = [[0 for x in range(self.sfw)] for y in range(self.sfh)]
#
#         self.mesh_tiles = [[MeshTile(
#             (self.ax + x * self.tile_size, self.ay + y * self.tile_size),
#             self.tile_size
#         ) for x in range(tlsize[0])] for y in range(tlsize[1])]
#
#         # Scalar mapping
#         self.scalar_to_tile_position_map = {
#             (0, 0): [(0, 0)],
#             (self.sfw - 1, 0): [(self.sfw - 2, 0)],
#             (self.sfw - 1, self.sfh - 1): [(self.sfw - 2, self.sfh - 2)],
#             (0, self.sfh - 1): [(0, self.sfh - 2)]
#         }
#         self.scalar_to_tile_position_map.update({(x, 0): [(x, 0), (x - 1, 0)] for x in range(1, self.sfw - 1)})
#         self.scalar_to_tile_position_map.update({(0, y): [(0, y), (0, y - 1)] for y in range(1, self.sfh - 1)})
#         self.scalar_to_tile_position_map.update(
#             {(x, self.sfh - 1): [(x, self.sfh - 2), (x - 1, self.sfh - 2)] for x in range(1, self.sfw - 1)})
#         self.scalar_to_tile_position_map.update(
#             {(self.sfw - 1, y): [(self.sfw - 2, y), (self.sfw - 2, y - 1)] for y in range(1, self.sfh - 1)})
#         self.scalar_to_tile_position_map.update({
#             (x, y): [(x, y), (x - 1, y), (x - 1, y - 1), (x, y - 1)] for y in range(1, self.sfh - 1) for x in
#             range(1, self.sfw - 1)
#         })
#
#         sprite_groups.add(self.mesh_tiles[y][x] for x in range(tlsize[0]) for y in range(tlsize[1]))
#
#     def reset(self):
#         self.scalar_field = [[0 for x in range(self.sfw)] for y in range(self.sfh)]
#         for y in range(self.sfh - 1):
#             for x in range(self.sfw - 1):
#                 self.mesh_tiles[y][x].set_state(0)
#
#     def add_to_scalar(self, sfpos: tuple[int, int], val: int):
#         old_val = self.scalar_field[sfpos[1]][sfpos[0]]
#         self.scalar_field[sfpos[1]][sfpos[0]] += val
#
#         if self.scalar_field[sfpos[1]][sfpos[0]] * old_val == 0:
#             for x, y in self.scalar_to_tile_position_map[sfpos]:
#                 self.mesh_tiles[y][x].set_state(
#                     (1 if self.scalar_field[y][x] else 0) |
#                     ((1 if self.scalar_field[y][x + 1] else 0) << 1) |
#                     ((1 if self.scalar_field[y + 1][x + 1] else 0) << 2) |
#                     ((1 if self.scalar_field[y + 1][x] else 0) << 3)
#                 )
#
#     def set_scalar(self, sfpos: tuple[int, int], val: int):
#         old_val = self.scalar_field[sfpos[1]][sfpos[0]]
#         self.scalar_field[sfpos[1]][sfpos[0]] = val
#
#         if self.scalar_field[sfpos[1]][sfpos[0]] * old_val == 0:
#             for x, y in self.scalar_to_tile_position_map[sfpos]:
#                 self.mesh_tiles[y][x].set_state(
#                     (1 if self.scalar_field[y][x] else 0) |
#                     ((1 if self.scalar_field[y][x + 1] else 0) << 1) |
#                     ((1 if self.scalar_field[y + 1][x + 1] else 0) << 2) |
#                     ((1 if self.scalar_field[y + 1][x] else 0) << 3)
#                 )
#
#     def get_scalar(self, sfpos: tuple[int, int]) -> int:
#         return self.scalar_field[sfpos[1]][sfpos[0]]
#
#     def generate_mesh_sprites(
#             self,
#             extrude_weight: float = 0.25,
#             color=(255, 255, 255),
#             stroke_weight: float = 1,
#             stroke_color=(255, 255, 255)
#     ):
#         w = np.clip(extrude_weight, 0.0, 0.99)
#         cw = 1 - w
#
#         if w == 0:
#             stroke_weight = 0
#
#         MeshGrid.state_sprite_map[0] = Surface((self.tile_size, self.tile_size), SRCALPHA)
#
#         surface = Surface((self.tile_size, self.tile_size), SRCALPHA)
#         Graphics.pie(
#             surface,
#             0, 0,
#             self.tile_size * w,
#             -HALF_PI, 0,
#             color, stroke_weight, stroke_color
#         )
#         MeshGrid.state_sprite_map[1] = surface
#
#         surface = Surface((self.tile_size, self.tile_size), SRCALPHA)
#         Graphics.pie(
#             surface,
#             self.tile_size, 0,
#             self.tile_size * w,
#             PI, PI * 1.5,
#             color, stroke_weight, stroke_color
#         )
#         MeshGrid.state_sprite_map[2] = surface
#
#         surface = Surface((self.tile_size, self.tile_size), SRCALPHA)
#         Graphics.rect(
#             surface,
#             (0, 0),
#             (self.tile_size, self.tile_size * w),
#             color
#         )
#         Graphics.line(
#             surface,
#             (0, self.tile_size * w),
#             (self.tile_size, self.tile_size * w),
#             stroke_weight, stroke_color
#         )
#         MeshGrid.state_sprite_map[3] = surface
#
#         surface = Surface((self.tile_size, self.tile_size), SRCALPHA)
#         Graphics.pie(
#             surface,
#             self.tile_size, self.tile_size,
#             self.tile_size * w,
#             HALF_PI, PI,
#             color, stroke_weight, stroke_color
#         )
#         MeshGrid.state_sprite_map[4] = surface
#
#         surface = Surface((self.tile_size, self.tile_size), SRCALPHA)
#         Graphics.pie(
#             surface,
#             0, 0,
#             self.tile_size * w,
#             -HALF_PI, 0,
#             color, stroke_weight, stroke_color
#         )
#         Graphics.pie(
#             surface,
#             self.tile_size, self.tile_size,
#             self.tile_size * w,
#             HALF_PI, PI,
#             color, stroke_weight, stroke_color
#         )
#         MeshGrid.state_sprite_map[5] = surface
#
#         surface = Surface((self.tile_size, self.tile_size), SRCALPHA)
#         Graphics.rect(
#             surface,
#             (self.tile_size * cw, 0),
#             (self.tile_size * w, self.tile_size),
#             color
#         )
#         Graphics.line(
#             surface,
#             (self.tile_size * cw, 0),
#             (self.tile_size * cw, self.tile_size),
#             stroke_weight, stroke_color
#         )
#         MeshGrid.state_sprite_map[6] = surface
#
#         surface = Surface((self.tile_size, self.tile_size), SRCALPHA)
#         Graphics.inverse_pie(
#             surface,
#             0, self.tile_size,
#             self.tile_size * cw, self.tile_size,
#             0, HALF_PI,
#             color, stroke_weight, stroke_color
#         )
#         MeshGrid.state_sprite_map[7] = surface
#
#         surface = Surface((self.tile_size, self.tile_size), SRCALPHA)
#         Graphics.pie(
#             surface,
#             0, self.tile_size,
#             self.tile_size * w,
#             0, HALF_PI,
#             color, stroke_weight, stroke_color
#         )
#         MeshGrid.state_sprite_map[8] = surface
#
#         surface = Surface((self.tile_size, self.tile_size), SRCALPHA)
#         Graphics.rect(
#             surface,
#             (0, 0),
#             (self.tile_size * w, self.tile_size),
#             color
#         )
#         Graphics.line(
#             surface,
#             (self.tile_size * w, 0),
#             (self.tile_size * w, self.tile_size),
#             stroke_weight, stroke_color
#         )
#         MeshGrid.state_sprite_map[9] = surface
#
#         surface = Surface((self.tile_size, self.tile_size), SRCALPHA)
#         Graphics.pie(
#             surface,
#             self.tile_size, 0,
#             self.tile_size * w,
#             PI, PI * 1.5,
#             color, stroke_weight, stroke_color
#         )
#         Graphics.pie(
#             surface,
#             0, self.tile_size,
#             self.tile_size * w,
#             0, HALF_PI,
#             color, stroke_weight, stroke_color
#         )
#         MeshGrid.state_sprite_map[10] = surface
#
#         surface = Surface((self.tile_size, self.tile_size), SRCALPHA)
#         Graphics.inverse_pie(
#             surface,
#             self.tile_size, self.tile_size,
#             self.tile_size * cw, self.tile_size,
#             HALF_PI, PI,
#             color, stroke_weight, stroke_color
#         )
#         MeshGrid.state_sprite_map[11] = surface
#
#         surface = Surface((self.tile_size, self.tile_size), SRCALPHA)
#         Graphics.rect(
#             surface,
#             (0, self.tile_size * cw),
#             (self.tile_size, self.tile_size * w),
#             color
#         )
#         Graphics.line(
#             surface,
#             (0, self.tile_size * cw),
#             (self.tile_size, self.tile_size * cw),
#             stroke_weight, stroke_color
#         )
#         MeshGrid.state_sprite_map[12] = surface
#
#         surface = Surface((self.tile_size, self.tile_size), SRCALPHA)
#         Graphics.inverse_pie(
#             surface,
#             self.tile_size, 0,
#             self.tile_size * cw, self.tile_size,
#             -PI, -HALF_PI,
#             color, stroke_weight, stroke_color
#         )
#         MeshGrid.state_sprite_map[13] = surface
#
#         surface = Surface((self.tile_size, self.tile_size), SRCALPHA)
#         Graphics.inverse_pie(
#             surface,
#             0, 0,
#             self.tile_size * cw, self.tile_size,
#             -HALF_PI, 0,
#             color, stroke_weight, stroke_color
#         )
#         MeshGrid.state_sprite_map[14] = surface
#
#         surface = Surface((self.tile_size, self.tile_size), SRCALPHA)
#         Graphics.rect(
#             surface,
#             (0, 0),
#             (self.tile_size, self.tile_size),
#             color
#         )
#         MeshGrid.state_sprite_map[15] = surface
#
#
# class MeshTile(DirtySprite):
#
#     def __init__(
#             self,
#             apos: tuple[float, float],
#             tile_size: float
#     ):
#         super().__init__()
#
#         self.state = 0
#
#         # Graphics properties
#         self.apos = self.ax, self.ay = apos
#         self.size = self.w, self.h = tile_size, tile_size
#         self.image = Surface(self.size, SRCALPHA)
#         self.rect = Rect(self.apos, self.size)
#
#     def set_state(self, state: int):
#         if self.state != state:
#             self.state = state
#             self.dirty = 1
#
#     def update(self):
#         if MeshGrid.state_sprite_map.get(self.state):
#             self.image = MeshGrid.state_sprite_map.get(self.state)

class SelectionTile(DirtySprite):

    def __init__(self, apos: tuple[float, float], size: tuple[float, float], sprite_groups: AbstractGroup):
        super().__init__(sprite_groups)
        self.apos = self.ax, self.ay = apos
        self.size = self.w, self.h = size

        self.rect = Rect(apos, size)
        self.image = Surface(size, SRCALPHA)

    def redraw(self, state: int):
        self.image = SelectionGrid.sprite_map[state]
        self.dirty = 1


class MeshGrid:
    """Holds and calculates the data needed to build a mesh base using Marching Square."""

    def __init__(self, state_size: tuple[int, int], bit_size: tuple[int, int]):
        """state_size: The size of the state grid
        bit_size: the size of the bit grid"""

        self.state_size = self.state_w, self.state_h = state_size
        self.bit_size = self.bit_w, self.bit_h = bit_size

        self._states = [[0 for _ in range(self.state_w)] for _ in range(self.state_h)]
        self.bits = [[0 for _ in range(self.bit_w)] for _ in range(self.bit_h)]

    @property
    def states(self):
        return self._states

    def reset(self):
        self._states = [[0 for _ in range(self.state_w)] for _ in range(self.state_h)]
        self.bits = [[0 for _ in range(self.bit_w)] for _ in range(self.bit_h)]

    def add(self, value: int, bit_pos: set[tuple[int, int]]) -> set[tuple[int, int]]:
        """Adds value to specified positions"""
        # Update bits and record affected states
        affected = set()
        for bx, by in bit_pos:
            self.bits[by][bx] += value
            affected |= self.bit_to_state(bx, by)

        # Update affected states
        for sx, sy in affected:
            self.update_state(sx, sy)

        return affected

    @cache
    def bit_to_state(self, bx, by) -> set[tuple[int, int]]:
        """Describes how bit position map to state position"""
        conditions = (
            bx > 0 and by > 0,
            by > 0 and bx < self.bit_w - 1,
            bx > 0 and by < self.bit_h - 1,
            bx < self.bit_w - 1 and by < self.bit_h
        )
        states_pos = ((bx - 1, by - 1), (bx, by - 1), (bx - 1, by), (bx, by))

        return {states_pos[_] for _ in range(4) if conditions[_]}

    def update_state(self, sx, sy):
        """Recalculates the specified state position"""
        self._states[sy][sx] = (1 if self.bits[sy][sx] > 0 else 0) | \
                               ((1 if self.bits[sy][sx + 1] > 0 else 0) << 1) | \
                               ((1 if self.bits[sy + 1][sx + 1] > 0 else 0) << 2) | \
                               ((1 if self.bits[sy + 1][sx] > 0 else 0) << 3)
