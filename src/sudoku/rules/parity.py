from pygame import Surface
from pygame.gfxdraw import filled_circle

from . import ComponentRule
from src.core.gfx import Graphics
from src.sudoku.tile import Tile


# ----- Data -----
class ParityRule(ComponentRule):

    def __init__(self, tile: tuple[int, int]):
        super().__init__([tile])
        self.value = 0

    def __new__(cls, *args, **kwargs):
        if cls is ParityRule:
            raise TypeError(f"Only childrens of {cls.__name__} shall be instantiated!")
        return super().__new__(cls)

    def update(self, pos: tuple[int, int], new_val: int, old_val: int):
        self.value = new_val


class EvenRule(ParityRule):
    weight = .75
    color = (150, 150, 150)

    def check(self) -> bool:
        return self.value and self.value % 2 == 0

    def draw(self, surface: Surface):
        bw = Tile.SIZE * (1 - EvenRule.weight) / 2
        Graphics.rect(
            surface,
            (Tile.SIZE * self.bound_to[0][0] + bw, Tile.SIZE * self.bound_to[0][1] + bw),
            (Tile.SIZE * EvenRule.weight, Tile.SIZE * EvenRule.weight),
            EvenRule.color
        )


class OddRule(ParityRule):
    weight = .75
    color = (150, 150, 150)

    def check(self) -> bool:
        return self.value % 2 != 0

    def draw(self, surface: Surface):
        filled_circle(
            surface,
            int(Tile.SIZE * self.bound_to[0][0] + Tile.SIZE / 2),
            int(Tile.SIZE * self.bound_to[0][1] + Tile.SIZE / 2),
            int(Tile.SIZE * OddRule.weight / 2),
            OddRule.color
        )
