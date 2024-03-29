from pygame import Surface
from pygame.gfxdraw import filled_circle

from .rule import ComponentRule
from core.gfx.graphics import Graphics
from maker.properties import Properties, PropertiesType, PropertiesError


# ----- Data -----
class ParityRule(ComponentRule):

    def __init__(self, tile: tuple[int, int] = (0, 0)):
        super().__init__([tile])
        self.value = 0

    def __new__(cls, *args, **kwargs):
        if cls is ParityRule:
            raise TypeError(f"Only childrens of {cls.__name__} shall be instantiated!")
        return super().__new__(cls)

    def update(self, pos: tuple[int, int], new_val: int, old_val: int):
        self.value = new_val
        print(f"[Parity Rule]: Current value = {self.value}.")

    def get_properties(self) -> list[Properties]:
        return [
            Properties("Tile", PropertiesType.POS, self.bound_to[0])
        ]

    def set_properties(self, *data):
        bound_to = data[0]

        # Validate data
        x, y = bound_to
        if x < 0 or y < 0 or x > 8 or y > 8:
            raise PropertiesError("Tiles must be within the board.")

        self.bound_to = [bound_to]


class EvenRule(ParityRule):
    DESCRIPTIONS = "Grey squares show even digits."

    weight = .75
    color = (150, 150, 150)

    def check(self) -> bool:
        return self.value and self.value % 2 == 0

    def draw(self, surface: Surface, tile_size: tuple[float, float]):
        bw = tile_size[0] * (1 - EvenRule.weight) / 2
        Graphics.rect(
            surface,
            (tile_size[0] * self.bound_to[0][0] + bw, tile_size[1] * self.bound_to[0][1] + bw),
            (tile_size[0] * EvenRule.weight, tile_size[1] * EvenRule.weight),
            EvenRule.color
        )


class OddRule(ParityRule):
    DESCRIPTIONS = "Grey circles show odd digits."

    weight = .75
    color = (150, 150, 150)

    def check(self) -> bool:
        return self.value % 2 != 0

    def draw(self, surface: Surface, tile_size: tuple[float, float]):
        filled_circle(
            surface,
            int((self.bound_to[0][0] + .5) * tile_size[0]),
            int((self.bound_to[0][1] + .5) * tile_size[1]),
            int(tile_size[0] * OddRule.weight / 2),
            OddRule.color
        )
