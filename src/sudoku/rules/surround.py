from pygame import Surface
from pygame.font import SysFont
from pygame.gfxdraw import filled_circle

from .rule import ComponentRule
from sudoku.tile import Tile
from maker.properties import Properties, PropertiesType, PropertiesError


# ----- Data -----
class SurroundRule(ComponentRule):
    font = SysFont("Arial", 10)
    color = (255, 255, 255)
    text_color = (0, 0, 0)

    def __init__(self, values: set[int] = None, tile: tuple[int, int] = (0, 0)):
        """values: Values that need to appear at least once (1 - 4 values)
        tile: The top left tile's position of the 2x2 grid"""
        super().__init__([
            tile, (tile[0] + 1, tile[1]),
            (tile[0], tile[1] + 1), (tile[0] + 1, tile[1] + 1)
        ])
        self.target = values or {1, 2, 3, 4}
        self.values = list()

        # For drawing
        self.pos = (tile[0] + 1, tile[1] + 1)

    def get_properties(self) -> list[Properties]:
        return [
            Properties("Values", PropertiesType.INT_LIST, self.target),
            Properties("Top left tile", PropertiesType.POS, self.bound_to[0])
        ]

    def set_properties(self, *data):
        values, tile = data

        values = set(values)
        if len(values) < 1 or len(values) > 4:
            raise PropertiesError("Number of values must be in range [1, 4].")
        for val in values:
            if val < 1 or val > 9:
                raise PropertiesError("Value must in the range [1, 9]")

        x, y = tile
        if x < 0 or y < 0 or x > 7 or y > 7:
            raise PropertiesError("Tiles surrounding the component must be within the board.")

        self.bound_to = [
            tile, (tile[0] + 1, tile[1]),
            (tile[0], tile[1] + 1), (tile[0] + 1, tile[1] + 1)
        ]
        self.pos = self.bound_to[-1]
        self.target = values

    def update(self, pos: tuple[int, int], new_val: int, old_val: int):
        if old_val:
            self.values.remove(old_val)
        if new_val:
            self.values.append(new_val)

    def check(self) -> bool:
        if len(self.values) < 4:
            return False
        return set(self.values) & self.target == self.target

    def draw(self, surface: Surface):
        pos = self.pos[0] * Tile.SIZE, self.pos[1] * Tile.SIZE
        filled_circle(surface, int(pos[0]), int(pos[1]), int(Tile.SIZE / 4), SurroundRule.color)

        texts = [SurroundRule.font.render(str(_), True, SurroundRule.text_color) for _ in self.target]
        disp = ((1, 1), (0, 1), (0, 0), (1, 0))
        for _ in range(len(texts)):
            surface.blit(
                texts[_],
                (pos[0] - disp[_][0] * texts[_].get_width(),
                 pos[1] - disp[_][1] * texts[_].get_height())
            )
