from pygame import Surface, SRCALPHA
from pygame.sprite import DirtySprite, LayeredDirty
from pygame.rect import Rect

import numpy as np

from functools import cache

from src.core.gfx.graphics import Graphics
from src.core.utils import HALF_PI, PI, MeshGrid
from .tile import Tile


class SelectionGrid:
    sprite_map = {}

    def __init__(
            self,
            apos: tuple[float, float],
            tlsize: tuple[int, int],
            sprite_groups: LayeredDirty
    ):
        self.apos = self.ax, self.ay = apos
        self.tlsize = self.tlw, self.tlh = tlsize
        self.selected = set()

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
        self.mesh_grid = SelectionMeshGrid(
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

        bw = self.spr_w * w

        self.sprite_map[0] = Surface(self.spr_size, SRCALPHA)
        self.sprite_map[5] = Surface(self.spr_size, SRCALPHA)
        self.sprite_map[10] = Surface(self.spr_size, SRCALPHA)

        surface = Surface(self.spr_size, SRCALPHA)
        Graphics.pie(
            surface,
            0, 0,
            bw,
            -HALF_PI, 0,
            color, stroke_weight, stroke_color
        )
        self.sprite_map[1] = surface

        surface = Surface(self.spr_size, SRCALPHA)
        Graphics.pie(
            surface,
            self.spr_w, 0,
            bw,
            PI, PI * 1.5,
            color, stroke_weight, stroke_color
        )
        self.sprite_map[2] = surface

        surface = Surface(self.spr_size, SRCALPHA)
        Graphics.rect(
            surface,
            (0, 0),
            (self.spr_w, bw),
            color
        )
        Graphics.line(
            surface,
            (0, self.spr_w * w),
            (self.spr_w, bw),
            stroke_weight, stroke_color
        )
        self.sprite_map[3] = surface

        surface = Surface(self.spr_size, SRCALPHA)
        Graphics.pie(
            surface,
            self.spr_w, self.spr_w,
            bw,
            HALF_PI, PI,
            color, stroke_weight, stroke_color
        )
        self.sprite_map[4] = surface

        surface = Surface(self.spr_size, SRCALPHA)
        Graphics.rect(
            surface,
            (self.spr_w - bw, 0),
            (bw, self.spr_w),
            color
        )
        Graphics.line(
            surface,
            (self.spr_w - bw, 0),
            (self.spr_w - bw, self.spr_w),
            stroke_weight, stroke_color
        )
        self.sprite_map[6] = surface

        surface = Surface(self.spr_size, SRCALPHA)
        Graphics.rect(
            surface,
            (0, 0),
            (max(0, self.spr_w - bw * 2), bw),
            color
        )
        Graphics.line(
            surface,
            (0, bw),
            (max(0, self.spr_w - bw * 2), bw),
            stroke_weight, stroke_color
        )
        Graphics.rect(
            surface,
            (self.spr_w - bw, min(2 * bw, self.spr_w)),
            (bw, max(0, self.spr_w - bw * 2)),
            color
        )
        Graphics.line(
            surface,
            (self.spr_w - bw, min(2 * bw, self.spr_w)),
            (self.spr_w - bw, self.spr_w),
            stroke_weight, stroke_color
        )
        Graphics.inverse_pie(
            surface,
            max(0, self.spr_w - bw * 2), min(2 * bw, self.spr_w),
            bw if 2 * bw < self.spr_w else self.spr_w - bw, min(2 * bw, self.spr_w),
            0, HALF_PI,
            color, stroke_weight, stroke_color
        )
        self.sprite_map[7] = surface

        surface = Surface(self.spr_size, SRCALPHA)
        Graphics.pie(
            surface,
            0, self.spr_w,
            bw,
            0, HALF_PI,
            color, stroke_weight, stroke_color
        )
        self.sprite_map[8] = surface

        surface = Surface(self.spr_size, SRCALPHA)
        Graphics.rect(
            surface,
            (0, 0),
            (bw, self.spr_w),
            color
        )
        Graphics.line(
            surface,
            (bw, 0),
            (bw, self.spr_w),
            stroke_weight, stroke_color
        )
        self.sprite_map[9] = surface

        surface = Surface(self.spr_size, SRCALPHA)
        Graphics.rect(
            surface,
            (min(2 * bw, self.spr_w), 0),
            (max(0, self.spr_w - bw * 2), bw),
            color
        )
        Graphics.line(
            surface,
            (min(2 * bw, self.spr_w), bw),
            (self.spr_w, bw),
            stroke_weight, stroke_color
        )
        Graphics.rect(
            surface,
            (0, min(2 * bw, self.spr_w)),
            (bw, max(0, self.spr_w - bw * 2)),
            color
        )
        Graphics.line(
            surface,
            (bw, min(2 * bw, self.spr_w)),
            (bw, self.spr_w),
            stroke_weight, stroke_color
        )
        Graphics.inverse_pie(
            surface,
            min(2 * bw, self.spr_w), min(2 * bw, self.spr_w),
            bw if 2 * bw < self.spr_w else self.spr_w - bw, min(2 * bw, self.spr_w),
            HALF_PI, PI,
            color, stroke_weight, stroke_color
        )
        self.sprite_map[11] = surface

        surface = Surface(self.spr_size, SRCALPHA)
        Graphics.rect(
            surface,
            (0, self.spr_w - bw),
            (self.spr_w, bw),
            color
        )
        Graphics.line(
            surface,
            (0, self.spr_w - bw),
            (self.spr_w, self.spr_w - bw),
            stroke_weight, stroke_color
        )
        self.sprite_map[12] = surface

        surface = Surface(self.spr_size, SRCALPHA)
        Graphics.rect(
            surface,
            (min(2 * bw, self.spr_w), self.spr_w - bw),
            (max(0, self.spr_w - bw * 2), bw),
            color
        )
        Graphics.line(
            surface,
            (min(2 * bw, self.spr_w), self.spr_w - bw),
            (self.spr_w, self.spr_w - bw),
            stroke_weight, stroke_color
        )
        Graphics.rect(
            surface,
            (0, 0),
            (bw, max(0, self.spr_w - bw * 2)),
            color
        )
        Graphics.line(
            surface,
            (bw, 0),
            (bw, max(0, self.spr_w - bw * 2)),
            stroke_weight, stroke_color
        )
        Graphics.inverse_pie(
            surface,
            min(2 * bw, self.spr_w), max(0, self.spr_w - bw * 2),
            bw if 2 * bw < self.spr_w else self.spr_w - bw, min(2 * bw, self.spr_w),
            -PI, -HALF_PI,
            color, stroke_weight, stroke_color
        )
        self.sprite_map[13] = surface

        surface = Surface(self.spr_size, SRCALPHA)
        Graphics.rect(
            surface,
            (0, self.spr_w - bw),
            (max(0, self.spr_w - bw * 2), bw),
            color
        )
        Graphics.line(
            surface,
            (0, self.spr_w - bw),
            (max(0, self.spr_w - bw * 2), self.spr_w - bw),
            stroke_weight, stroke_color
        )
        Graphics.rect(
            surface,
            (self.spr_w - bw, 0),
            (bw, max(0, self.spr_w - bw * 2)),
            color
        )
        Graphics.line(
            surface,
            (self.spr_w - bw, 0),
            (self.spr_w - bw, max(0, self.spr_w - bw * 2)),
            stroke_weight, stroke_color
        )
        Graphics.inverse_pie(
            surface,
            max(0, self.spr_w - bw * 2), max(0, self.spr_w - bw * 2),
            bw if 2 * bw < self.spr_w else self.spr_w - bw, min(2 * bw, self.spr_w),
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


class SelectionTile(DirtySprite):

    def __init__(self, apos: tuple[float, float], size: tuple[float, float], sprite_groups: LayeredDirty):
        super().__init__()
        self.apos = self.ax, self.ay = apos
        self.size = self.w, self.h = size

        self.rect = Rect(apos, size)
        self.image = Surface(size, SRCALPHA)
        sprite_groups.add(self, layer=5)

    def redraw(self, state: int):
        self.image = SelectionGrid.sprite_map[state]
        self.dirty = 1


class SelectionMeshGrid(MeshGrid):

    @cache
    def bit_to_state(self, bx, by) -> set[tuple[int, int]]:
        conditions = (
            bx > 0 and by > 0,
            by > 0 and bx < self.bit_w - 1,
            bx > 0 and by < self.bit_h - 1,
            bx < self.bit_w - 1 and by < self.bit_h
        )
        states_pos = ((bx - 1, by - 1), (bx, by - 1), (bx - 1, by), (bx, by))

        return {states_pos[_] for _ in range(4) if conditions[_]}

    def update_state(self, sx, sy):
        self._states[sy][sx] = (1 if self.bits[sy][sx] > 0 else 0) | \
                               ((1 if self.bits[sy][sx + 1] > 0 else 0) << 1) | \
                               ((1 if self.bits[sy + 1][sx + 1] > 0 else 0) << 2) | \
                               ((1 if self.bits[sy + 1][sx] > 0 else 0) << 3)
