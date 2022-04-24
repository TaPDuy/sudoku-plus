from pygame import Surface
from pygame.gfxdraw import aaellipse

import numpy as np

from .rule import ComponentRule
from core.gfx.graphics import Graphics
from sudoku.tile import Tile
from maker.properties import Properties


# ----- Data -----
class ArrowRule(ComponentRule):
    color = (255, 255, 255)

    def __init__(self, bound_to: list[tuple[int, int]]):
        super().__init__(bound_to)
        self.target = 0
        self.sum = 0

    def update(self, pos: tuple[int, int], new_val: int, old_val: int):
        if pos == self.bound_to[0]:
            self.target = new_val
        else:
            self.sum = self.sum - old_val + new_val

    def check(self) -> bool:
        return self.sum == self.target != 0

    def get_properties(self) -> list[Properties]:
        pass

    def set_properties(self, *data):
        pass

    def draw(self, surface: Surface):
        org = self.bound_to[0][0] * Tile.SIZE + Tile.SIZE / 2, \
              self.bound_to[0][1] * Tile.SIZE + Tile.SIZE / 2
        aaellipse(
            surface,
            int(org[0]), int(org[1]),
            int(Tile.SIZE * 3 / 8), int(Tile.SIZE * 3 / 8),
            ArrowRule.color
        )

        tile1 = self.bound_to[1][0] * Tile.SIZE + Tile.SIZE / 2, \
                self.bound_to[1][1] * Tile.SIZE + Tile.SIZE / 2
        vec = np.asarray(tile1) - np.asarray(org)
        unit = vec / np.linalg.norm(vec)
        Graphics.arrow_lines(
            surface,
            [org + Tile.SIZE * 3 / 8 * unit] + [(
                x * Tile.SIZE + Tile.SIZE / 2, y * Tile.SIZE + Tile.SIZE / 2
            ) for x, y in self.bound_to[1:]]
        )
