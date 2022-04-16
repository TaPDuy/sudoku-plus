from functools import cache

import numpy as np

from pygame import Surface, SRCALPHA
from pygame.font import SysFont

from src.core.gfx import Graphics
from src.core.utils import MeshGrid
from . import ComponentRule
from src.sudoku.tile import Tile


# ----- Data -----
class KillerRule(ComponentRule):
    killer_tile_size = killer_tile_w, killer_tile_h = Tile.SIZE / 2, Tile.SIZE / 2
    killer_sprites = {}
    font = SysFont("Arial", 10)
    color = (255, 255, 255)
    weight: float = .75
    dash_len: float = 4.0
    gap_len: float = 4.0
    stroke_weight: int = 1

    def __init__(self, target_sum: int = 0, bound_to: set = None):
        super().__init__(bound_to)

        self.sum = 0
        self.target = target_sum

    def update(self, pos: tuple[int, int], new_val: int, old_val: int):
        super()._check_conflict(pos, new_val, old_val)
        self.sum = self.sum - old_val + new_val

    def check(self) -> bool:
        return self.sum == self.target and len(self.conflicts) == 0

    def get_properties(self) -> dict[str, str]:
        return {
            "target_sum": "Sum",
            "bound_to": "Cage tiles"
        }

    def get_properties_value(self, property_id: str) -> object | None:
        match property_id:
            case "target_sum":
                return self.target
            case "bound_to":
                return self.bound_to

    def get_properties_value_string(self, property_id: str) -> str:
        match property_id:
            case "target_sum":
                return str(self.target)
            case "bound_to":
                return ", ".join(str(_) for _ in self.bound_to) if self.bound_to else ""

    def set_properties(self, property_id: str, value):
        match property_id:
            case "target_sum":
                if type(value) is not int:
                    raise ValueError("Cage sum must be int.")

                self.target = value
            case "bound_to":
                if type(value) not in (list, set, tuple):
                    raise ValueError("Cage tiles must be tuple of 2D position.")
                value = set(value)
                if any(type(_) is not tuple or len(_) != 2 for _ in value):
                    raise ValueError("Cage tiles must be tuple of 2D position.")
                if len(value) <= 0 or len(value) > 9:
                    raise ValueError("Number of cage tiles must be from 1-9.")

                self.bound_to = value

    def draw(self, surface: Surface):
        top_left = min(self.bound_to, key=lambda x: x[0])[0], min(self.bound_to, key=lambda x: x[1])[1]
        ptop_left = top_left[0] * Tile.SIZE, top_left[1] * Tile.SIZE
        width = max(self.bound_to, key=lambda x: x[0])[0] - top_left[0] + 1
        height = max(self.bound_to, key=lambda x: x[1])[1] - top_left[1] + 1

        mesh_grid = KillerMeshGrid((width << 1, height << 1), ((width << 1) + 1, (height << 1) + 1))
        for x, y in self.bound_to:
            conditions = (
                (x + 1, y) in self.bound_to,
                (x, y + 1) in self.bound_to,
                (x + 1, y) in self.bound_to and (x, y + 1) in self.bound_to and (x + 1, y + 1) in self.bound_to
            )
            x -= top_left[0]
            y -= top_left[1]
            states_pos = ((x + 1 << 1, (y << 1) + 1), ((x << 1) + 1, y + 1 << 1), (x + 1 << 1, y + 1 << 1))

            mesh_grid.add(1, {states_pos[_] for _ in range(3) if conditions[_]} | {((x << 1) + 1, (y << 1) + 1)})

        surface.blits(
            tuple((
                      KillerRule.killer_sprites[mesh_grid.states[y][x]],
                      (x * KillerRule.killer_tile_w + ptop_left[0], y * KillerRule.killer_tile_h + ptop_left[1])
                  ) for y in range(mesh_grid.state_h) for x in range(mesh_grid.state_w))
        )

        sum_tile = min(self.bound_to)
        text = KillerRule.font.render(str(self.target), True, KillerRule.color)
        # text = smoothscale(text, (text.get_width() * Tile.SIZE / 64, text.get_height() * Tile.SIZE / 64))
        surface.blit(text, (
            (sum_tile[0] + 0.125) * KillerRule.killer_tile_w * 2,
            (sum_tile[1] + 0.125) * KillerRule.killer_tile_h * 2
        ))

    @staticmethod
    def generate_killer_mesh():
        w = np.clip(KillerRule.weight, 0.01, 1.0)
        bw, bh = (KillerRule.killer_tile_w * (1 - w)) / 2, (KillerRule.killer_tile_h * (1 - w)) / 2
        btl, btr, bbr, bbl = (bw, bh), \
                             (KillerRule.killer_tile_w - bw, bh), \
                             (KillerRule.killer_tile_w - bw, KillerRule.killer_tile_h - bh), \
                             (bw, KillerRule.killer_tile_h - bh)

        KillerRule.killer_sprites[0] = Surface(KillerRule.killer_tile_size, SRCALPHA)
        KillerRule.killer_sprites[5] = Surface(KillerRule.killer_tile_size, SRCALPHA)
        KillerRule.killer_sprites[10] = Surface(KillerRule.killer_tile_size, SRCALPHA)
        KillerRule.killer_sprites[15] = Surface(KillerRule.killer_tile_size, SRCALPHA)

        surface = Surface(KillerRule.killer_tile_size, SRCALPHA)
        Graphics.dashed_lines(surface, [
            (btr[0], 0), bbr, (0, bbl[1])
        ], KillerRule.dash_len, KillerRule.gap_len, KillerRule.stroke_weight, KillerRule.color)
        KillerRule.killer_sprites[1] = surface

        surface = Surface(KillerRule.killer_tile_size, SRCALPHA)
        Graphics.dashed_lines(surface, [
            (KillerRule.killer_tile_w, bbr[1]), bbl, (btl[0], 0)
        ], KillerRule.dash_len, KillerRule.gap_len, KillerRule.stroke_weight, KillerRule.color)
        KillerRule.killer_sprites[2] = surface

        surface = Surface(KillerRule.killer_tile_size, SRCALPHA)
        Graphics.dashed_line(
            surface,
            (KillerRule.killer_tile_w, bbr[1]), (0, bbl[1]),
            KillerRule.dash_len, KillerRule.gap_len,
            KillerRule.stroke_weight, KillerRule.color
        )
        KillerRule.killer_sprites[3] = surface

        surface = Surface(KillerRule.killer_tile_size, SRCALPHA)
        Graphics.dashed_lines(surface, [
            (bbl[0], KillerRule.killer_tile_h), btl, (KillerRule.killer_tile_w, btr[1])
        ], KillerRule.dash_len, KillerRule.gap_len, KillerRule.stroke_weight, KillerRule.color)
        KillerRule.killer_sprites[4] = surface

        surface = Surface(KillerRule.killer_tile_size, SRCALPHA)
        Graphics.dashed_line(
            surface,
            (bbl[0], KillerRule.killer_tile_h), (btl[0], 0),
            KillerRule.dash_len, KillerRule.gap_len,
            KillerRule.stroke_weight, KillerRule.color
        )
        KillerRule.killer_sprites[6] = surface

        surface = Surface(KillerRule.killer_tile_size, SRCALPHA)
        Graphics.dashed_lines(surface, [
            (bbl[0], KillerRule.killer_tile_h), bbl, (0, bbl[1])
        ], KillerRule.dash_len, KillerRule.gap_len, KillerRule.stroke_weight, KillerRule.color)
        KillerRule.killer_sprites[7] = surface

        surface = Surface(KillerRule.killer_tile_size, SRCALPHA)
        Graphics.dashed_lines(surface, [
            (0, btl[1]), btr, (bbr[0], KillerRule.killer_tile_h)
        ], KillerRule.dash_len, KillerRule.gap_len, KillerRule.stroke_weight, KillerRule.color)
        KillerRule.killer_sprites[8] = surface

        surface = Surface(KillerRule.killer_tile_size, SRCALPHA)
        Graphics.dashed_line(
            surface,
            (btr[0], 0), (bbr[0], KillerRule.killer_tile_h),
            KillerRule.dash_len, KillerRule.gap_len,
            KillerRule.stroke_weight, KillerRule.color
        )
        KillerRule.killer_sprites[9] = surface

        surface = Surface(KillerRule.killer_tile_size, SRCALPHA)
        Graphics.dashed_lines(surface, [
            (KillerRule.killer_tile_w, bbr[1]), bbr, (bbr[0], KillerRule.killer_tile_h)
        ], KillerRule.dash_len, KillerRule.gap_len, KillerRule.stroke_weight, KillerRule.color)
        KillerRule.killer_sprites[11] = surface

        surface = Surface(KillerRule.killer_tile_size, SRCALPHA)
        Graphics.dashed_line(
            surface,
            (0, btl[1]), (KillerRule.killer_tile_w, btr[1]),
            KillerRule.dash_len, KillerRule.gap_len,
            KillerRule.stroke_weight, KillerRule.color
        )
        KillerRule.killer_sprites[12] = surface

        surface = Surface(KillerRule.killer_tile_size, SRCALPHA)
        Graphics.dashed_lines(surface, [
            (btr[0], 0), btr, (KillerRule.killer_tile_w, btr[1])
        ], KillerRule.dash_len, KillerRule.gap_len, KillerRule.stroke_weight, KillerRule.color)
        KillerRule.killer_sprites[13] = surface

        surface = Surface(KillerRule.killer_tile_size, SRCALPHA)
        Graphics.dashed_lines(surface, [
            (0, btl[1]), btl, (btl[0], 0)
        ], KillerRule.dash_len, KillerRule.gap_len, KillerRule.stroke_weight, KillerRule.color)
        KillerRule.killer_sprites[14] = surface


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
