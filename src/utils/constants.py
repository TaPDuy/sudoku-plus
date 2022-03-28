from enum import Enum
from numpy import pi

PI = pi
HALF_PI = pi * 0.5
QUARTER_PI = pi * 0.25
TWO_PI = pi * 2


class InputMode(Enum):
    INPUT_MODE_VALUE = 0
    INPUT_MODE_MARK = 1
    INPUT_MODE_COLOR = 2
