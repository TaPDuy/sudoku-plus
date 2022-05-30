from functools import cache

import numpy as np

from pygame import Surface, SRCALPHA
from pygame.transform import smoothscale
from pygame.font import SysFont

from core.gfx.graphics import Graphics
from core.utils.mesh import MeshGrid
from .rule import ComponentRule
from maker.properties import Properties, PropertiesType, PropertiesError


# ----- Data -----
class KillerRule(ComponentRule):
    DESCRIPTIONS = "In cages, digits must sum to the small clue (if exists) in the top left corner of the cage. " \
                   "Digits cannot repeat within a cage."

    # killer_tile_size = killer_tile_w, killer_tile_h = Tile.SIZE / 2, Tile.SIZE / 2
    killer_sprites = {}
    font = SysFont("Arial", 10)
    color = (255, 255, 255)
    # weight: float = .75
    # dash_len: float = 4.0
    # gap_len: float = 4.0
    # stroke_weight: int = 1

    def __init__(self, target_sum: int = 1, bound_to: set = None):
        super().__init__(bound_to)
        if not bound_to:
            self.bound_to = {(0, 0)}

        self.sum = 0
        self.target = target_sum

    def update(self, pos: tuple[int, int], new_val: int, old_val: int):
        self.sum = self.sum - old_val + new_val
        print(f"[Killer Rule]: Current sum = {self.sum}, target sum = {self.target}.")

    def conflict(self, p1: tuple[int, int], p2: tuple[int, int]) -> bool:
        return p1 in self.bound_to and p2 in self.bound_to

    def check(self) -> bool:
        return self.sum == self.target if self.target else True

    def get_properties(self) -> list[Properties]:
        return [
            Properties("Target sum", PropertiesType.INT, self.target),
            Properties("Cage tiles", PropertiesType.POS_LIST, self.bound_to)
        ]

    def set_properties(self, *data):
        target_sum, bound_to = data
        bound_to = set(bound_to)

        # Validate data
        n_tiles = len(bound_to)
        if n_tiles < 1 or n_tiles > 9:
            raise PropertiesError("Number of cage tiles must be in range [1, 9].")

        mn, mx = sum(i for i in range(1, n_tiles + 1)), sum(9 - i for i in range(n_tiles))
        if (target_sum < mn or target_sum > mx) and target_sum != 0:
            raise PropertiesError(f"Target sum must be either in range [{mn}, {mx}] or 0.")

        dx, dy = (0, 1, 0, -1), (1, 0, -1, 0)
        for x, y in bound_to:
            if x < 0 or y < 0 or x > 8 or y > 8:
                raise PropertiesError("Cage tiles must be within the board.")
            if n_tiles > 1 and all((x + dx[_], y + dy[_]) not in bound_to for _ in range(4)):
                raise PropertiesError("Cage tiles must touch each other's sides.")

        self.target = target_sum
        self.bound_to = bound_to

    def draw(self, surface: Surface, tile_size: tuple[float, float]):
        top_left = min(self.bound_to, key=lambda x: x[0])[0], min(self.bound_to, key=lambda x: x[1])[1]
        ptop_left = top_left[0] * tile_size[0], top_left[1] * tile_size[1]
        width = max(self.bound_to, key=lambda x: x[0])[0] - top_left[0] + 1
        height = max(self.bound_to, key=lambda x: x[1])[1] - top_left[1] + 1

        mesh_grid = KillerMeshGrid((width << 1, height << 1))
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

        killer_tile_size = tile_size[0] / 2, tile_size[1] / 2
        surface.blits(tuple((
            smoothscale(KillerRule.killer_sprites[mesh_grid.states[y][x]], killer_tile_size),
            (x * killer_tile_size[0] + ptop_left[0], y * killer_tile_size[1] + ptop_left[1])
        ) for y in range(mesh_grid.state_h) for x in range(mesh_grid.state_w)))

        if self.target:
            sum_tile = min(self.bound_to)
            text = KillerRule.font.render(str(self.target), True, KillerRule.color)
            # text = smoothscale(text, (text.get_width() * Tile.SIZE / 64, text.get_height() * Tile.SIZE / 64))
            surface.blit(text, (
                (sum_tile[0] + 0.125) * tile_size[0],
                (sum_tile[1] + 0.125) * tile_size[1]
            ))

    @staticmethod
    def generate_killer_mesh(
            tile_render_size: tuple[float, float],
            weight: float = .7,
            dash_len: float = 5.0,
            gap_len: float = 5.0,
            color: tuple[int, int, int] = (255, 255, 255),
            stroke_weight: int = 2
    ):
        w = np.clip(weight, 0.01, 1.0)
        bw, bh = (tile_render_size[0] * (1 - w)) / 2, (tile_render_size[1] * (1 - w)) / 2
        btl, btr, bbr, bbl = (bw, bh), \
                             (tile_render_size[0] - bw, bh), \
                             (tile_render_size[0] - bw, tile_render_size[1] - bh), \
                             (bw, tile_render_size[1] - bh)

        KillerRule.killer_sprites[0] = Surface(tile_render_size, SRCALPHA)
        KillerRule.killer_sprites[5] = Surface(tile_render_size, SRCALPHA)
        KillerRule.killer_sprites[10] = Surface(tile_render_size, SRCALPHA)
        KillerRule.killer_sprites[15] = Surface(tile_render_size, SRCALPHA)

        surface = Surface(tile_render_size, SRCALPHA)
        Graphics.dashed_lines(surface, [
            (btr[0], 0), bbr, (0, bbl[1])
        ], dash_len, gap_len, stroke_weight, color)
        KillerRule.killer_sprites[1] = surface

        surface = Surface(tile_render_size, SRCALPHA)
        Graphics.dashed_lines(surface, [
            (tile_render_size[0], bbr[1]), bbl, (btl[0], 0)
        ], dash_len, gap_len, stroke_weight, color)
        KillerRule.killer_sprites[2] = surface

        surface = Surface(tile_render_size, SRCALPHA)
        Graphics.dashed_line(
            surface,
            (tile_render_size[0], bbr[1]), (0, bbl[1]),
            dash_len, gap_len,
            stroke_weight, color
        )
        KillerRule.killer_sprites[3] = surface

        surface = Surface(tile_render_size, SRCALPHA)
        Graphics.dashed_lines(surface, [
            (bbl[0], tile_render_size[1]), btl, (tile_render_size[0], btr[1])
        ], dash_len, gap_len, stroke_weight, color)
        KillerRule.killer_sprites[4] = surface

        surface = Surface(tile_render_size, SRCALPHA)
        Graphics.dashed_line(
            surface,
            (bbl[0], tile_render_size[1]), (btl[0], 0),
            dash_len, gap_len,
            stroke_weight, color
        )
        KillerRule.killer_sprites[6] = surface

        surface = Surface(tile_render_size, SRCALPHA)
        Graphics.dashed_lines(surface, [
            (bbl[0], tile_render_size[1]), bbl, (0, bbl[1])
        ], dash_len, gap_len, stroke_weight, color)
        KillerRule.killer_sprites[7] = surface

        surface = Surface(tile_render_size, SRCALPHA)
        Graphics.dashed_lines(surface, [
            (0, btl[1]), btr, (bbr[0], tile_render_size[1])
        ], dash_len, gap_len, stroke_weight, color)
        KillerRule.killer_sprites[8] = surface

        surface = Surface(tile_render_size, SRCALPHA)
        Graphics.dashed_line(
            surface,
            (btr[0], 0), (bbr[0], tile_render_size[1]),
            dash_len, gap_len,
            stroke_weight, color
        )
        KillerRule.killer_sprites[9] = surface

        surface = Surface(tile_render_size, SRCALPHA)
        Graphics.dashed_lines(surface, [
            (tile_render_size[0], bbr[1]), bbr, (bbr[0], tile_render_size[1])
        ], dash_len, gap_len, stroke_weight, color)
        KillerRule.killer_sprites[11] = surface

        surface = Surface(tile_render_size, SRCALPHA)
        Graphics.dashed_line(
            surface,
            (0, btl[1]), (tile_render_size[0], btr[1]),
            dash_len, gap_len,
            stroke_weight, color
        )
        KillerRule.killer_sprites[12] = surface

        surface = Surface(tile_render_size, SRCALPHA)
        Graphics.dashed_lines(surface, [
            (btr[0], 0), btr, (tile_render_size[0], btr[1])
        ], dash_len, gap_len, stroke_weight, color)
        KillerRule.killer_sprites[13] = surface

        surface = Surface(tile_render_size, SRCALPHA)
        Graphics.dashed_lines(surface, [
            (0, btl[1]), btl, (btl[0], 0)
        ], dash_len, gap_len, stroke_weight, color)
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
