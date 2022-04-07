from pygame import Surface

import numpy as np

from . import ComponentRule
from src.core.gfx import Graphics


# ----- Data -----
class PalindromeRule(ComponentRule):

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


# ----- Graphics -----
def palindrome(
    surface: Surface,
    rule: PalindromeRule
):
    Graphics.smooth_lines(surface, [
        (x * 48 + 24, y * 48 + 24) for x, y in rule.bound_to
    ], 12, (100, 100, 100))
