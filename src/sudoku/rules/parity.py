from pygame import Surface
from pygame.gfxdraw import filled_circle

from . import ComponentRule
from src.core.gfx import Graphics


# ----- Data -----
class EvenRule(ComponentRule):

    def __init__(self, tile: tuple[int, int]):
        super().__init__([tile])
        self.value = 0

    def update(self, pos: tuple[int, int], new_val: int, old_val: int):
        self.value = new_val

    def check(self) -> bool:
        return self.value and self.value % 2 == 0


class OddRule(ComponentRule):

    def __init__(self, tile: tuple[int, int]):
        super().__init__([tile])
        self.value = 0

    def update(self, pos: tuple[int, int], new_val: int, old_val: int):
        self.value = new_val

    def check(self) -> bool:
        return self.value % 2 != 0


# ----- Graphics -----
def even(
        surface: Surface,
        rule: EvenRule
):
    bw = 48 * .25 / 2
    Graphics.rect(
        surface,
        (48 * rule.bound_to[0][0] + bw, 48 * rule.bound_to[0][1] + bw),
        (48 * .75, 48 * .75),
        (150, 150, 150)
    )


def odd(
        surface: Surface,
        rule: OddRule
):
    filled_circle(
        surface,
        48 * rule.bound_to[0][0] + 24, 48 * rule.bound_to[0][1] + 24,
        int(48 * .75 / 2),
        (150, 150, 150)
    )
