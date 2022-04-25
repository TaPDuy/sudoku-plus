from pygame import Surface
from pygame.gfxdraw import filled_circle, aacircle

from .rule import ComponentRule
from src.sudoku.tile import Tile
from maker.properties import Properties, PropertiesType, PropertiesError


# ----- Data -----
class DotRule(ComponentRule):

    def __init__(self, tile1: tuple[int, int] = (0, 0), tile2: tuple[int, int] = (1, 0)):
        super().__init__([tile1, tile2])
        self.values = [0, 0]

    def __new__(cls, *args, **kwargs):
        if cls is DotRule:
            raise TypeError(f"Only childrens of {cls.__name__} shall be instantiated!")
        return super().__new__(cls)

    def update(self, pos: tuple[int, int], new_val: int, old_val: int):
        self.values[self.bound_to.index(pos)] = new_val

    def get_properties(self) -> list[Properties]:
        return [
            Properties("Tile 1", PropertiesType.POS, self.bound_to[0]),
            Properties("Tile 2", PropertiesType.POS, self.bound_to[1])
        ]

    def set_properties(self, *data):
        tile1, tile2 = data

        # Validate data
        x1, y1 = tile1
        if x1 < 0 or y1 < 0 or x1 > 8 or y1 > 8:
            raise PropertiesError("Tile 1 must be within the board.")
        x2, y2 = tile2
        if x2 < 0 or y2 < 0 or x2 > 8 or y2 > 8:
            raise PropertiesError("Tile 2 must be within the board.")
        if abs(x2 - x1) + abs(y2 - y1) != 1:
            raise PropertiesError("Tile 1 and 2 must be orthogonally next to each other.")

        self.bound_to = [tile1, tile2]


class BlackDotRule(DotRule):
    color = (0, 0, 0)
    stroke_color = (255, 255, 255)

    def check(self) -> bool:
        if 0 in self.values:
            return False
        return self.values[0] / self.values[1] in (2, .5)

    def draw(self, surface: Surface):
        x, y = (self.bound_to[0][0] + self.bound_to[1][0]) / 2, (self.bound_to[0][1] + self.bound_to[1][1]) / 2
        filled_circle(
            surface,
            int((x + .5) * Tile.SIZE), int((y + .5) * Tile.SIZE),
            int(Tile.SIZE / 8),
            BlackDotRule.color
        )
        aacircle(
            surface,
            int((x + .5) * Tile.SIZE), int((y + .5) * Tile.SIZE),
            int(Tile.SIZE / 8),
            BlackDotRule.stroke_color
        )


class WhiteDotRule(DotRule):
    color = (255, 255, 255)
    stroke_color = (0, 0, 0)

    def check(self) -> bool:
        if 0 in self.values:
            return False
        return abs(self.values[0] - self.values[1]) == 1

    def draw(self, surface: Surface):
        x, y = (self.bound_to[0][0] + self.bound_to[1][0]) / 2, (self.bound_to[0][1] + self.bound_to[1][1]) / 2
        filled_circle(
            surface,
            int((x + .5) * Tile.SIZE), int((y + .5) * Tile.SIZE),
            int(Tile.SIZE / 8),
            WhiteDotRule.color
        )
        aacircle(
            surface,
            int((x + .5) * Tile.SIZE), int((y + .5) * Tile.SIZE),
            int(Tile.SIZE / 8),
            WhiteDotRule.stroke_color
        )
