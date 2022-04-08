from pygame import Surface

import numpy as np

from . import ComponentRule
from src.core.gfx import Graphics
from src.sudoku.tile import Tile


# ----- Data -----
class PalindromeRule(ComponentRule):
    color = (100, 100, 100)

    def __init__(self, bound_to: list[tuple[int, int]]):
        super().__init__(bound_to)
        self.length = len(bound_to)
        self.values = [0 for _ in np.arange(self.length)]

    def update(self, pos: tuple[int, int], new_val: int, old_val: int):
        index = self.bound_to.index(pos)
        self.values[index] = new_val

    def check(self) -> bool:
        if 0 in self.values:
            return False
        return all(self.values[i] == self.values[-1 - i] for i in np.arange(self.length >> 1))

    def draw(self, surface: Surface):
        Graphics.smooth_lines(surface, [
            (x * Tile.SIZE + Tile.SIZE / 2, y * Tile.SIZE + Tile.SIZE / 2) for x, y in self.bound_to
        ], Tile.SIZE / 4, PalindromeRule.color)
