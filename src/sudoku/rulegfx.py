from functools import cache

import numpy as np

from pygame import Surface, SRCALPHA
from pygame.font import SysFont

from ..core.gfx import Graphics
from ..core.utils import MeshGrid
from .rule import KillerRule


killer_tile_size = killer_tile_w, killer_tile_h = 24, 24
killer_sprites = {}


def killer_sudoku(
        surface: Surface,
        rule: KillerRule
):
    width = max(rule.bound_to, key=lambda x: x[0])[0] - min(rule.bound_to, key=lambda x: x[0])[0] + 1
    height = max(rule.bound_to, key=lambda x: x[1])[1] - min(rule.bound_to, key=lambda x: x[1])[1] + 1

    mesh_grid = KillerMeshGrid((width << 1, height << 1), ((width << 1) + 1, (height << 1) + 1))
    for x, y in rule.bound_to:
        conditions = (
            (x + 1, y) in rule.bound_to,
            (x, y + 1) in rule.bound_to,
            (x + 1, y) in rule.bound_to and (x, y + 1) in rule.bound_to and (x + 1, y + 1) in rule.bound_to
        )
        states_pos = ((x + 1 << 1, (y << 1) + 1), ((x << 1) + 1, y + 1 << 1), (x + 1 << 1, y + 1 << 1))

        mesh_grid.add(1, {states_pos[_] for _ in range(3) if conditions[_]} | {((x << 1) + 1, (y << 1) + 1)})

    surface.blits(
        tuple((
                  killer_sprites[mesh_grid.states[y][x]],
                  (x * killer_tile_w, y * killer_tile_h)
              ) for y in range(mesh_grid.state_h) for x in range(mesh_grid.state_w))
    )

    font = SysFont("Arial", 10)
    sum_tile = min(rule.bound_to)
    text = font.render(str(rule.target), True, (255, 255, 255))
    # text = smoothscale(text, (text.get_width() * Tile.SIZE / 64, text.get_height() * Tile.SIZE / 64))
    surface.blit(text, (
        (sum_tile[0] + 0.125) * killer_tile_w,
        (sum_tile[1] + 0.125) * killer_tile_h
    ))


def generate_killer_mesh(
        weight: float = .75,
        dash_len: float = 4, gap_len: float = 4,
        stroke_weight: int = 1,
        stroke_color: tuple[int, int, int, int] = (255, 255, 255, 255)
):
    w = np.clip(weight, 0.01, 1.0)
    bw, bh = (killer_tile_w * (1 - w)) / 2, (killer_tile_h * (1 - w)) / 2
    btl, btr, bbr, bbl = (bw, bh), (killer_tile_w - bw, bh), (killer_tile_w - bw, killer_tile_h - bh), (bw, killer_tile_h - bh)

    killer_sprites[0] = Surface(killer_tile_size, SRCALPHA)
    killer_sprites[5] = Surface(killer_tile_size, SRCALPHA)
    killer_sprites[10] = Surface(killer_tile_size, SRCALPHA)
    killer_sprites[15] = Surface(killer_tile_size, SRCALPHA)

    surface = Surface(killer_tile_size, SRCALPHA)
    Graphics.dashed_lines(surface, [
        (btr[0], 0), bbr, (0, bbl[1])
    ], dash_len, gap_len, stroke_weight, stroke_color)
    killer_sprites[1] = surface

    surface = Surface(killer_tile_size, SRCALPHA)
    Graphics.dashed_lines(surface, [
        (killer_tile_w, bbr[1]), bbl, (btl[0], 0)
    ], dash_len, gap_len, stroke_weight, stroke_color)
    killer_sprites[2] = surface

    surface = Surface(killer_tile_size, SRCALPHA)
    Graphics.dashed_line(surface, (killer_tile_w, bbr[1]), (0, bbl[1]), dash_len, gap_len, stroke_weight, stroke_color)
    killer_sprites[3] = surface

    surface = Surface(killer_tile_size, SRCALPHA)
    Graphics.dashed_lines(surface, [
        (bbl[0], killer_tile_h), btl, (killer_tile_w, btr[1])
    ], dash_len, gap_len, stroke_weight, stroke_color)
    killer_sprites[4] = surface

    surface = Surface(killer_tile_size, SRCALPHA)
    Graphics.dashed_line(surface, (bbl[0], killer_tile_h), (btl[0], 0), dash_len, gap_len, stroke_weight, stroke_color)
    killer_sprites[6] = surface

    surface = Surface(killer_tile_size, SRCALPHA)
    Graphics.dashed_lines(surface, [
        (bbl[0], killer_tile_h), bbl, (0, bbl[1])
    ], dash_len, gap_len, stroke_weight, stroke_color)
    killer_sprites[7] = surface

    surface = Surface(killer_tile_size, SRCALPHA)
    Graphics.dashed_lines(surface, [
        (0, btl[1]), btr, (bbr[0], killer_tile_h)
    ], dash_len, gap_len, stroke_weight, stroke_color)
    killer_sprites[8] = surface

    surface = Surface(killer_tile_size, SRCALPHA)
    Graphics.dashed_line(surface, (btr[0], 0), (bbr[0], killer_tile_h), dash_len, gap_len, stroke_weight, stroke_color)
    killer_sprites[9] = surface

    surface = Surface(killer_tile_size, SRCALPHA)
    Graphics.dashed_lines(surface, [
        (killer_tile_w, bbr[1]), bbr, (bbr[0], killer_tile_h)
    ], dash_len, gap_len, stroke_weight, stroke_color)
    killer_sprites[11] = surface

    surface = Surface(killer_tile_size, SRCALPHA)
    Graphics.dashed_line(surface, (0, btl[1]), (killer_tile_w, btr[1]), dash_len, gap_len, stroke_weight, stroke_color)
    killer_sprites[12] = surface

    surface = Surface(killer_tile_size, SRCALPHA)
    Graphics.dashed_lines(surface, [
        (btr[0], 0), btr, (killer_tile_w, btr[1])
    ], dash_len, gap_len, stroke_weight, stroke_color)
    killer_sprites[13] = surface

    surface = Surface(killer_tile_size, SRCALPHA)
    Graphics.dashed_lines(surface, [
        (0, btl[1]), btl, (btl[0], 0)
    ], dash_len, gap_len, stroke_weight, stroke_color)
    killer_sprites[14] = surface


class KillerMeshGrid(MeshGrid):

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
