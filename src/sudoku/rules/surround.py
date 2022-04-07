from pygame import Surface
from pygame.font import SysFont
from pygame.gfxdraw import filled_circle

from . import ComponentRule


# ----- Data -----
class SurroundRule(ComponentRule):

    def __init__(self, values: set[int], tile: tuple[int, int]):
        """values: Values that need to appear at least once (1 - 4 values)
        tile: The top left tile's position of the 2x2 grid"""
        super().__init__([
            tile, (tile[0] + 1, tile[1]),
            (tile[0], tile[1] + 1), (tile[0] + 1, tile[1] + 1)
        ])
        self.values = list()
        self.target = values

        # For drawing
        self.pos = (tile[0] + 1, tile[1] + 1)

    def update(self, pos: tuple[int, int], new_val: int, old_val: int):
        if old_val:
            self.values.remove(old_val)
        if new_val:
            self.values.append(new_val)

    def check(self) -> bool:
        if len(self.values) < 4:
            return False
        return set(self.values) & self.target == self.target


# ----- Graphics -----
def surround(
        surface: Surface,
        rule: SurroundRule
):
    tile_size = 48
    pos = rule.pos[0] * tile_size, rule.pos[1] * tile_size
    filled_circle(surface, int(pos[0]), int(pos[1]), int(tile_size / 4), (255, 255, 255))

    font = SysFont("Arial", 10)
    texts = [font.render(str(_), True, (0, 0, 0)) for _ in rule.target]
    disp = ((1, 1), (0, 1), (0, 0), (1, 0))
    for _ in range(len(texts)):
        surface.blit(texts[_], (pos[0] - disp[_][0] * texts[_].get_width(), pos[1] - disp[_][1] * texts[_].get_height()))
