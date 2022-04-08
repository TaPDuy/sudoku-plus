from .rules import Rule


class Level:

    def __init__(self, rules: set[Rule], initial: dict[tuple[int, int], int]):
        """
        A class that holds all the data needed to load a level.
        :param rules: Ruleset that determines winning conditions
        :param initial: Initial clues - dict[(tile_x, tile_y): value]
        """
        self.__rules = rules
        self.__initial = initial

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
