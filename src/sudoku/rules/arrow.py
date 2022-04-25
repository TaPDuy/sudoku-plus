from pygame import Surface
from pygame.gfxdraw import aaellipse

import numpy as np

from .rule import ComponentRule
from core.gfx.graphics import Graphics
from sudoku.tile import Tile
from maker.properties import Properties, PropertiesType, PropertiesError


# ----- Data -----
class ArrowRule(ComponentRule):
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
