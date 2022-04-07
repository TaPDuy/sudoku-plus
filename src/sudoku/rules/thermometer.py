from pygame import Surface

import numpy as np

from . import ComponentRule
from src.core.utils import TWO_PI
from src.core.gfx import Graphics


# ----- Data -----
class ThermometerRule(ComponentRule):

    def __init__(self, bound_to: list[tuple[int, int]]):
        super().__init__(bound_to)
        self.length = len(bound_to)
        self.values = [0 for _ in np.arange(self.length)]
        self.error = 0

    def update(self, pos: tuple[int, int], new_val: int, old_val: int):
        index = self.bound_to.index(pos)
        self.values[index] = new_val
        print(self.values)

    def check(self) -> bool:
        if 0 in self.values:
            return False
        return all(self.values[i - 1] < self.values[i] for i in np.arange(1, self.length))


# ----- Graphics -----
def thermometer(
        surface: Surface,
        rule: ThermometerRule
):
    org = rule.bound_to[0][0] * 48 + 24, rule.bound_to[0][1] * 48 + 24
    Graphics.pie(surface, org[0], org[1], 18, 0, TWO_PI, (150, 150, 150), 0)
    Graphics.smooth_lines(surface, [
        (x * 48 + 24, y * 48 + 24) for x, y in rule.bound_to
    ], 18, (150, 150, 150))
