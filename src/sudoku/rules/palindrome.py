from pygame import Surface

import numpy as np

from .rule import ComponentRule
from core.gfx.graphics import Graphics
from maker.properties import Properties, PropertiesType, PropertiesError


# ----- Data -----
class PalindromeRule(ComponentRule):
    DESCRIPTIONS = "Digits along the lines are palindromes."

    color = (100, 100, 100)

    def __init__(self, bound_to: list[tuple[int, int]] = None):
        super().__init__(bound_to)
        if not bound_to:
            self.bound_to = [(0, 0), (1, 0)]

        self.length = len(self.bound_to)
        self.values = [0 for _ in np.arange(self.length)]

    def update(self, pos: tuple[int, int], new_val: int, old_val: int):
        index = self.bound_to.index(pos)
        self.values[index] = new_val
        print(f"[Palindrome Rule]: Current values = {self.values}.")

    def check(self) -> bool:
        if 0 in self.values:
            return False
        return all(self.values[i] == self.values[-1 - i] for i in np.arange(self.length >> 1))

    def get_properties(self) -> list[Properties]:
        return [
            Properties("Path tiles", PropertiesType.POS_LIST, self.bound_to)
        ]

    def set_properties(self, *data):
        bound_to = list(dict.fromkeys(data[0]))

        # Validate data
        n_tiles = len(bound_to)
        if n_tiles < 2:
            raise PropertiesError("Number of tiles must be 2 or more.")

        x, y = bound_to[0]
        if x < 0 or y < 0 or x > 8 or y > 8:
            raise PropertiesError("Tiles must be within the board.")

        for i in range(n_tiles - 1):
            x1, y1 = bound_to[i]
            x2, y2 = bound_to[i + 1]

            if x2 < 0 or y2 < 0 or x2 > 8 or y2 > 8:
                raise PropertiesError("Tiles must be within the board.")

            if (abs(x2 - x1), abs(y2 - y1)) not in ((0, 1), (1, 0), (1, 1)):
                raise PropertiesError("Tiles must be next to each other and form a path (in order).")

        self.bound_to = bound_to
        self.length = len(self.bound_to)
        self.values = [0 for _ in np.arange(self.length)]

    def draw(self, surface: Surface, tile_size: tuple[float, float]):
        Graphics.smooth_lines(surface, [
            ((x + .5) * tile_size[0], (y + .5) * tile_size[1]) for x, y in self.bound_to
        ], tile_size[0] / 4, PalindromeRule.color)
