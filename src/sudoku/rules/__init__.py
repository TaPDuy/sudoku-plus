from .rule import ComponentRule, GlobalRule, RuleManager

from .killer import killer_sudoku, generate_killer_mesh, KillerRule
from .arrow import arrow, ArrowRule
from .thermometer import ThermometerRule, thermometer
from .palindrome import PalindromeRule, palindrome
from .parity import EvenRule, OddRule, even, odd
from .dots import WhiteDotRule, BlackDotRule, black_dot, white_dot
from .surround import SurroundRule, surround

from .global_rules import *
