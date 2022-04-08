from pygame import Surface

import numpy as np

from . import ComponentRule
from src.core.utils import TWO_PI
from src.core.gfx import Graphics
from src.sudoku import Tile


# ----- Data -----
class ThermometerRule(ComponentRule):
    color = (150, 150, 150)

    def __init__(self, bound_to: list[tuple[int, int]]):
        super().__init__(bound_to)
        self.length = len(bound_to)
        self.values = [0 for _ in np.arange(self.length)]
        self.error = 0

    def update(self, pos: tuple[int, int], new_val: int, old_val: int):
        index = self.bound_to.index(pos)
        self.values[index] = new_val

    def check(self) -> bool:
        if 0 in self.values:
            return False
        return all(self.values[i - 1] < self.values[i] for i in np.arange(1, self.length))

    def draw(self, surface: Surface):
        org = self.bound_to[0][0] * Tile.SIZE + Tile.SIZE / 2, self.bound_to[0][1] * Tile.SIZE + Tile.SIZE / 2
        Graphics.pie(surface, org[0], org[1], Tile.SIZE * 3 / 8, 0, TWO_PI, ThermometerRule.color, 0)
        Graphics.smooth_lines(surface, [
            (x * Tile.SIZE + Tile.SIZE / 2, y * Tile.SIZE + Tile.SIZE / 2) for x, y in self.bound_to
        ], Tile.SIZE * 3 / 8, ThermometerRule.color)
