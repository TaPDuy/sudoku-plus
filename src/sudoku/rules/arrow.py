from pygame import Surface
from pygame.gfxdraw import aaellipse

import numpy as np

from . import ComponentRule
from src.core.gfx import Graphics


# ----- Data -----
class ArrowRule(ComponentRule):

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


# ----- Graphics -----
def arrow(
        surface: Surface,
        rule: ArrowRule
):
    org = rule.sum_tile[0] * 48 + 24, rule.sum_tile[1] * 48 + 24
    aaellipse(
        surface,
        org[0], org[1],
        18, 18, (255, 255, 255)
    )

    tile1 = rule.summand_tiles[0][0] * 48 + 24, rule.summand_tiles[0][1] * 48 + 24
    vec = np.asarray(tile1) - np.asarray(org)
    unit = vec / np.linalg.norm(vec)
    Graphics.arrow_lines(
        surface,
        [org + 18 * unit] + [(x * 48 + 24, y * 48 + 24) for x, y in rule.summand_tiles]
    )
