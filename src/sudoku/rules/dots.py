from pygame import Surface
from pygame.gfxdraw import filled_circle, aacircle

from .rule import ComponentRule
from src.sudoku.tile import Tile


# ----- Data -----
class DotRule(ComponentRule):

    def __init__(self, tile: tuple[int, int], edge: int):
        """tile: Position of the tile the dot is on\n
        edge: Index of tile's edges (0: North, 1: East, 2: South, 3: West)"""
        super().__init__([tile, (tile[0] + (0, 1, 0, -1)[edge], tile[1] + (-1, 0, 1, 0)[edge])])
        self.edge = edge
        self.values = [0, 0]

    def __new__(cls, *args, **kwargs):
        if cls is DotRule:
            raise TypeError(f"Only childrens of {cls.__name__} shall be instantiated!")
        return super().__new__(cls)

    def update(self, pos: tuple[int, int], new_val: int, old_val: int):
        self.values[self.bound_to.index(pos)] = new_val


class BlackDotRule(DotRule):
    color = (0, 0, 0)
    stroke_color = (255, 255, 255)

    def check(self) -> bool:
        if 0 in self.values:
            return False
        return self.values[0] / self.values[1] in (2, .5)

    def draw(self, surface: Surface):
        dx, dy = (Tile.SIZE / 2, Tile.SIZE, Tile.SIZE / 2, 0)[self.edge], \
                 (0, Tile.SIZE / 2, Tile.SIZE, Tile.SIZE / 2)[self.edge]
        filled_circle(
            surface,
            int(self.bound_to[0][0] * Tile.SIZE + dx), int(self.bound_to[0][1] * Tile.SIZE + dy),
            int(Tile.SIZE / 8),
            BlackDotRule.color
        )
        aacircle(
            surface,
            int(self.bound_to[0][0] * Tile.SIZE + dx), int(self.bound_to[0][1] * Tile.SIZE + dy),
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
        dx, dy = (Tile.SIZE / 2, Tile.SIZE, Tile.SIZE / 2, 0)[self.edge], \
                 (0, Tile.SIZE / 2, Tile.SIZE, Tile.SIZE / 2)[self.edge]
        filled_circle(
            surface,
            int(self.bound_to[0][0] * Tile.SIZE + dx), int(self.bound_to[0][1] * Tile.SIZE + dy),
            int(Tile.SIZE / 8),
            WhiteDotRule.color
        )
        aacircle(
            surface,
            int(self.bound_to[0][0] * Tile.SIZE + dx), int(self.bound_to[0][1] * Tile.SIZE + dy),
            int(Tile.SIZE / 8),
            WhiteDotRule.stroke_color
        )
