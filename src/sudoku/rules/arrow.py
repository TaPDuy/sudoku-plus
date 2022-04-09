from pygame import Surface
from pygame.gfxdraw import aaellipse

import numpy as np

from . import ComponentRule
from src.core.gfx import Graphics
from src.sudoku.tile import Tile


# ----- Data -----
class ArrowRule(ComponentRule):
    color = (255, 255, 255)

    def __init__(self, sum_tile: tuple[int, int], summands: list[tuple[int, int]]):
        super().__init__({sum_tile} | set(summands))
        self.sum_tile = sum_tile
        self.summand_tiles = summands
        self.target = 0
        self.sum = 0

    def update(self, pos: tuple[int, int], new_val: int, old_val: int):
        if pos == self.sum_tile:
            self.target = new_val
        else:
            self.sum = self.sum - old_val + new_val

    def check(self) -> bool:
        return self.sum == self.target != 0

    def draw(self, surface: Surface):
        org = self.sum_tile[0] * Tile.SIZE + Tile.SIZE / 2, \
              self.sum_tile[1] * Tile.SIZE + Tile.SIZE / 2
        aaellipse(
            surface,
            int(org[0]), int(org[1]),
            int(Tile.SIZE * 3 / 8), int(Tile.SIZE * 3 / 8),
            ArrowRule.color
        )

        tile1 = self.summand_tiles[0][0] * Tile.SIZE + Tile.SIZE / 2, \
                self.summand_tiles[0][1] * Tile.SIZE + Tile.SIZE / 2
        vec = np.asarray(tile1) - np.asarray(org)
        unit = vec / np.linalg.norm(vec)
        Graphics.arrow_lines(
            surface,
            [org + Tile.SIZE * 3 / 8 * unit] + [(
                x * Tile.SIZE + Tile.SIZE / 2, y * Tile.SIZE + Tile.SIZE / 2
            ) for x, y in self.summand_tiles]
        )
