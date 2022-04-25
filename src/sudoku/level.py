import random
import numpy as np

from .rules.rule import Rule
from .rules.global_rules import SudokuRule


class Level:

    def __init__(self, rules: set[Rule] = None, initial: dict[tuple[int, int], int] = None):
        """
        A class that holds all the data needed to load a level.
        :param rules: Ruleset that determines winning conditions
        :param initial: Initial clues - dict[(tile_x, tile_y): value]
        """
        self.__rules = rules or set()
        self.__initial = initial or {}

    @property
    def rules(self):
        return self.__rules

    @property
    def start_values(self):
        return self.__initial

    def add_rule(self, rules: set[Rule] | Rule):
        if isinstance(rules, set):
            self.__rules |= rules
        else:
            self.__rules.add(rules)

    def set_start_value(self, pos: tuple[int, int], value: int):
        self.__initial[pos] = value

    def __str__(self):
        return f"""
        [
            ruleset=[
                {self.__rules}
            ],
            initial={self.__initial}
        ]
        """

    def __repr__(self):
        return f"""
        class='{self.__class__}', 
        data={self.__str__()}
        """


SEEDS = (
    "___bf_g_a|fh__g__i_|ai___de__|hb_a___d_|__df_bi__|_e___c_bh|__ic___gd|_d__e__cf|g_c_ah___",
    "a__dhi__f|gc_____d_|_____abie|__gab_f__|e__g_c__h|__f_ieg__|iadf_____|_b_____cg|h__eab__d",
    "_b_f_h___|eh___ig__|____d____|cg____e__|f_______d|__h____ac|____b____|__ih___cf|___c_f_i_",
    "___f__d__|g____cf__|____ia_h_|_________|_e_ah___c|___c_f_de|_d_b___f_|i_c______|_b____a__",
    "b__c_____|h_d_fb__c|_ach__b__|____b_ci_|e_g___fba|_cb__f___|_b___iad_|f_abe_h_i|_____a__b",
    "_b_______|___f____c|_gd_h____|_____c__b|_h__d__a_|f__e_____|____a_gh_|e____i___|_______d_"
)


def random_sudoku() -> Level:
    values = [_ for _ in range(1, 10)]
    random.shuffle(values)
    charmap = {chr(ord('a') + _): values[_] for _ in range(9)}

    seed = random.choice(SEEDS)
    print(f"Generating level from seed '{seed}'")

    chars = np.array([list(_) for _ in seed.split('|')])
    for _ in np.arange(random.randint(0, 3)):
        chars = np.rot90(chars)

    if random.getrandbits(1):
        chars = np.flip(chars, random.randint(0, 1))

    return Level(
        {SudokuRule()},
        {(x, y): charmap[chars[y][x]] for y in range(9) for x in range(9) if chars[y][x] != '_'}
    )
