from pygame import Surface
from pygame.gfxdraw import aaellipse

import numpy as np

from .rule import ComponentRule
from core.gfx.graphics import Graphics
from maker.properties import Properties, PropertiesType, PropertiesError


# ----- Data -----
class ArrowRule(ComponentRule):
    DESCRIPTIONS = "Digits along an arrow must sum to the digit in that arrow's circle."

    color = (255, 255, 255)

    def __init__(self, bound_to: list[tuple[int, int]] = None):
        super().__init__(bound_to)
        if not bound_to:
            self.bound_to = [(0, 0), (1, 0)]

        self.target = 0
        self.sum = 0

    def update(self, pos: tuple[int, int], new_val: int, old_val: int):
        if pos == self.bound_to[0]:
            self.target = new_val
        else:
            self.sum = self.sum - old_val + new_val
        print(f"[Arrow Rule]: Current sum = {self.sum}, target sum = {self.target}.")

    def check(self) -> bool:
        return self.sum == self.target != 0

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

    def draw(self, surface: Surface, tile_size: tuple[float, float]):
        org = (self.bound_to[0][0] + .5) * tile_size[0], (self.bound_to[0][1] + .5) * tile_size[1]
        aaellipse(
            surface,
            int(org[0]), int(org[1]),
            int(tile_size[0] * 3 / 8), int(tile_size[1] * 3 / 8),
            ArrowRule.color
        )

        tile1 = (self.bound_to[1][0] + .5) * tile_size[0], (self.bound_to[1][1] + .5) * tile_size[1]
        vec = np.asarray(tile1) - np.asarray(org)
        unit = vec / np.linalg.norm(vec)
        Graphics.arrow_lines(
            surface,
            [org + tile_size[0] * 3 / 8 * unit] + [(
                (x + .5) * tile_size[0], (y + .5) * tile_size[1]
            ) for x, y in self.bound_to[1:]]
        )
