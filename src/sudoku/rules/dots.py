from pygame import Surface
from pygame.gfxdraw import filled_circle, aacircle

from . import ComponentRule


# ----- Data -----
class BlackDotRule(ComponentRule):

    def __init__(self, tile: tuple[int, int], edge: int):
        """tile: Position of the tile the dot is on\n
        edge: Index of tile's edges (0: North, 1: East, 2: South, 3: West)"""
        super().__init__([tile, (tile[0] + (0, 1, 0, -1)[edge], tile[1] + (-1, 0, 1, 0)[edge])])
        self.edge = edge
        self.values = [0, 0]

    def update(self, pos: tuple[int, int], new_val: int, old_val: int):
        self.values[self.bound_to.index(pos)] = new_val

    def check(self) -> bool:
        if 0 in self.values:
            return False
        return self.values[0] / self.values[1] in (2, .5)


class WhiteDotRule(ComponentRule):

    def __init__(self, tile: tuple[int, int], edge: int):
        """tile: Position of the tile the dot is on\n
        edge: Index of tile's edges (0: North, 1: East, 2: South, 3: West)"""
        super().__init__([tile, (tile[0] + (0, 1, 0, -1)[edge], tile[1] + (-1, 0, 1, 0)[edge])])
        self.edge = edge
        self.values = [0, 0]

    def update(self, pos: tuple[int, int], new_val: int, old_val: int):
        self.values[self.bound_to.index(pos)] = new_val

    def check(self) -> bool:
        if 0 in self.values:
            return False
        return abs(self.values[0] - self.values[1]) == 1


# ----- Graphics -----
def black_dot(
        surface: Surface,
        rule: BlackDotRule
):
    tile_size = 48
    dx, dy = (tile_size / 2, tile_size, tile_size / 2, 0)[rule.edge], \
             (0, tile_size / 2, tile_size, tile_size / 2)[rule.edge]
    filled_circle(
        surface,
        int(rule.bound_to[0][0] * tile_size + dx), int(rule.bound_to[0][1] * tile_size + dy),
        int(tile_size / 8),
        (0, 0, 0)
    )
    aacircle(
        surface,
        int(rule.bound_to[0][0] * tile_size + dx), int(rule.bound_to[0][1] * tile_size + dy),
        int(tile_size / 8),
        (255, 255, 255)
    )


def white_dot(
        surface: Surface,
        rule: WhiteDotRule
):
    tile_size = 48
    dx, dy = (tile_size / 2, tile_size, tile_size / 2, 0)[rule.edge], \
             (0, tile_size / 2, tile_size, tile_size / 2)[rule.edge]
    filled_circle(
        surface,
        int(rule.bound_to[0][0] * tile_size + dx), int(rule.bound_to[0][1] * tile_size + dy),
        int(tile_size / 8),
        (255, 255, 255)
    )
    aacircle(
        surface,
        int(rule.bound_to[0][0] * tile_size + dx), int(rule.bound_to[0][1] * tile_size + dy),
        int(tile_size / 8),
        (0, 0, 0)
    )
