from pygame import Surface, SRCALPHA
from pygame.sprite import DirtySprite
from pygame.rect import Rect
from pygame.transform import smoothscale

import numpy as np

from functools import cache

from core.gfx.graphics import Graphics
from core.utils.constants import HALF_PI, PI
from core.utils.mesh import MeshGrid


class SelectionGrid(DirtySprite):
    sprite_map = {}

    def __init__(self, rect: Rect, container=None):
        super().__init__()

        # Graphics properties
        self.container = container
        self.tile_size = self.tlw, self.tlh = int(rect.w / 20), int(rect.h / 20)
        self.render_tile_size = self.render_tlw, self.render_tlh = self.tlw // 2, self.tlh // 2
        self.rect = self.relative_rect = rect
        if container:
            self.rect = Rect(
                (container.rect.x + self.rect.left, container.rect.y + self.rect.top),
                self.rect.size
            )

        self.mesh_grid = SelectionMeshGrid((20, 20))
        self.image = Surface(self.rect.size, SRCALPHA)
        self.__original_image = Surface((self.render_tlw * 20, self.render_tlh * 20), SRCALPHA)

        # Properties
        self.selected = set()

    def set_relative_rect(self, rect: Rect):
        self.tile_size = self.tlw, self.tlh = int(rect.w / 20), int(rect.h / 20)
        self.rect = self.relative_rect = rect
        if self.container:
            self.rect = Rect(
                (self.container.rect.x + self.rect.left, self.container.rect.y + self.rect.top),
                self.rect.size
            )

        self.dirty = 1
        self.image = smoothscale(self.__original_image, self.rect.size)

    def clear(self):
        self.selected.clear()
        self.mesh_grid.reset()
        self.image.fill((0, 0, 0, 0))
        self.__original_image.fill((0, 0, 0, 0))
        self.dirty = 1

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
            self.draw_tile(x, y)

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
            self.draw_tile(x, y)

        self.selected.remove(tlpos)

    def draw_tile(self, tlx, tly):
        state = self.mesh_grid.states[tly][tlx]
        pxpos = tlx * self.render_tlw, tly * self.render_tlh

        self.dirty = 1
        self.__original_image.fill((0, 0, 0, 0), Rect(pxpos, self.render_tile_size))
        self.__original_image.blit(SelectionGrid.sprite_map[state], pxpos)
        self.image = smoothscale(self.__original_image, self.rect.size)

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

        spr_size = spr_w, spr_h = self.render_tile_size
        bw = spr_w * w

        SelectionGrid.sprite_map[0] = Surface(spr_size, SRCALPHA)
        SelectionGrid.sprite_map[5] = Surface(spr_size, SRCALPHA)
        SelectionGrid.sprite_map[10] = Surface(spr_size, SRCALPHA)

        surface = Surface(spr_size, SRCALPHA)
        Graphics.pie(
            surface,
            0, 0,
            bw,
            -HALF_PI, 0,
            color, stroke_weight, stroke_color
        )
        SelectionGrid.sprite_map[1] = surface

        surface = Surface(spr_size, SRCALPHA)
        Graphics.pie(
            surface,
            spr_w, 0,
            bw,
            PI, PI * 1.5,
            color, stroke_weight, stroke_color
        )
        SelectionGrid.sprite_map[2] = surface

        surface = Surface(spr_size, SRCALPHA)
        Graphics.rect(
            surface,
            (0, 0),
            (spr_w, bw),
            color
        )
        Graphics.line(
            surface,
            (0, spr_w * w),
            (spr_w, bw),
            stroke_weight, stroke_color
        )
        SelectionGrid.sprite_map[3] = surface

        surface = Surface(spr_size, SRCALPHA)
        Graphics.pie(
            surface,
            spr_w, spr_w,
            bw,
            HALF_PI, PI,
            color, stroke_weight, stroke_color
        )
        SelectionGrid.sprite_map[4] = surface

        surface = Surface(spr_size, SRCALPHA)
        Graphics.rect(
            surface,
            (spr_w - bw, 0),
            (bw, spr_w),
            color
        )
        Graphics.line(
            surface,
            (spr_w - bw, 0),
            (spr_w - bw, spr_w),
            stroke_weight, stroke_color
        )
        SelectionGrid.sprite_map[6] = surface

        surface = Surface(spr_size, SRCALPHA)
        Graphics.rect(
            surface,
            (0, 0),
            (max(0, spr_w - bw * 2), bw),
            color
        )
        Graphics.line(
            surface,
            (0, bw),
            (max(0, spr_w - bw * 2), bw),
            stroke_weight, stroke_color
        )
        Graphics.rect(
            surface,
            (spr_w - bw, min(2 * bw, spr_w)),
            (bw, max(0, spr_w - bw * 2)),
            color
        )
        Graphics.line(
            surface,
            (spr_w - bw, min(2 * bw, spr_w)),
            (spr_w - bw, spr_w),
            stroke_weight, stroke_color
        )
        Graphics.inverse_pie(
            surface,
            max(0, spr_w - bw * 2), min(2 * bw, spr_w),
            bw if 2 * bw < spr_w else spr_w - bw, min(2 * bw, spr_w),
            0, HALF_PI,
            color, stroke_weight, stroke_color
        )
        SelectionGrid.sprite_map[7] = surface

        surface = Surface(spr_size, SRCALPHA)
        Graphics.pie(
            surface,
            0, spr_w,
            bw,
            0, HALF_PI,
            color, stroke_weight, stroke_color
        )
        SelectionGrid.sprite_map[8] = surface

        surface = Surface(spr_size, SRCALPHA)
        Graphics.rect(
            surface,
            (0, 0),
            (bw, spr_w),
            color
        )
        Graphics.line(
            surface,
            (bw, 0),
            (bw, spr_w),
            stroke_weight, stroke_color
        )
        SelectionGrid.sprite_map[9] = surface

        surface = Surface(spr_size, SRCALPHA)
        Graphics.rect(
            surface,
            (min(2 * bw, spr_w), 0),
            (max(0, spr_w - bw * 2), bw),
            color
        )
        Graphics.line(
            surface,
            (min(2 * bw, spr_w), bw),
            (spr_w, bw),
            stroke_weight, stroke_color
        )
        Graphics.rect(
            surface,
            (0, min(2 * bw, spr_w)),
            (bw, max(0, spr_w - bw * 2)),
            color
        )
        Graphics.line(
            surface,
            (bw, min(2 * bw, spr_w)),
            (bw, spr_w),
            stroke_weight, stroke_color
        )
        Graphics.inverse_pie(
            surface,
            min(2 * bw, spr_w), min(2 * bw, spr_w),
            bw if 2 * bw < spr_w else spr_w - bw, min(2 * bw, spr_w),
            HALF_PI, PI,
            color, stroke_weight, stroke_color
        )
        SelectionGrid.sprite_map[11] = surface

        surface = Surface(spr_size, SRCALPHA)
        Graphics.rect(
            surface,
            (0, spr_w - bw),
            (spr_w, bw),
            color
        )
        Graphics.line(
            surface,
            (0, spr_w - bw),
            (spr_w, spr_w - bw),
            stroke_weight, stroke_color
        )
        SelectionGrid.sprite_map[12] = surface

        surface = Surface(spr_size, SRCALPHA)
        Graphics.rect(
            surface,
            (min(2 * bw, spr_w), spr_w - bw),
            (max(0, spr_w - bw * 2), bw),
            color
        )
        Graphics.line(
            surface,
            (min(2 * bw, spr_w), spr_w - bw),
            (spr_w, spr_w - bw),
            stroke_weight, stroke_color
        )
        Graphics.rect(
            surface,
            (0, 0),
            (bw, max(0, spr_w - bw * 2)),
            color
        )
        Graphics.line(
            surface,
            (bw, 0),
            (bw, max(0, spr_w - bw * 2)),
            stroke_weight, stroke_color
        )
        Graphics.inverse_pie(
            surface,
            min(2 * bw, spr_w), max(0, spr_w - bw * 2),
            bw if 2 * bw < spr_w else spr_w - bw, min(2 * bw, spr_w),
            -PI, -HALF_PI,
            color, stroke_weight, stroke_color
        )
        SelectionGrid.sprite_map[13] = surface

        surface = Surface(spr_size, SRCALPHA)
        Graphics.rect(
            surface,
            (0, spr_w - bw),
            (max(0, spr_w - bw * 2), bw),
            color
        )
        Graphics.line(
            surface,
            (0, spr_w - bw),
            (max(0, spr_w - bw * 2), spr_w - bw),
            stroke_weight, stroke_color
        )
        Graphics.rect(
            surface,
            (spr_w - bw, 0),
            (bw, max(0, spr_w - bw * 2)),
            color
        )
        Graphics.line(
            surface,
            (spr_w - bw, 0),
            (spr_w - bw, max(0, spr_w - bw * 2)),
            stroke_weight, stroke_color
        )
        Graphics.inverse_pie(
            surface,
            max(0, spr_w - bw * 2), max(0, spr_w - bw * 2),
            bw if 2 * bw < spr_w else spr_w - bw, min(2 * bw, spr_w),
            -HALF_PI, 0,
            color, stroke_weight, stroke_color
        )
        SelectionGrid.sprite_map[14] = surface

        surface = Surface(spr_size, SRCALPHA)
        # surface.fill(color)
        Graphics.rect(
            surface,
            (0, 0),
            (spr_w, spr_h),
            color
        )
        SelectionGrid.sprite_map[15] = surface


# class SelectionTile(DirtySprite):
#
#     def __init__(self, apos: tuple[float, float], size: tuple[float, float], sprite_groups: LayeredDirty):
#         super().__init__()
#         self.apos = self.ax, self.ay = apos
#         self.size = self.w, self.h = size
#
#         self.rect = Rect(apos, size)
#         self.image = Surface(size, SRCALPHA)
#         sprite_groups.add(self, layer=5)
#
#     def redraw(self, state: int):
#         self.image = SelectionGrid.sprite_map[state]
#         self.dirty = 1


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
