class Rule:

    def conflict(self, *args) -> bool:
        pass


class GlobalRule(Rule):
    pass


class ComponentRule(Rule):
    pass


class ColumnRule(GlobalRule):

    def conflict(self, p1: tuple[int, int], p2: tuple[int, int]) -> bool:
        return p1[0] == p2[0]


class RowRule(GlobalRule):

    def conflict(self, p1: tuple[int, int], p2: tuple[int, int]) -> bool:
        return p1[1] == p2[1]


class BoxRule(GlobalRule):

    def conflict(self, p1: tuple[int, int], p2: tuple[int, int]) -> bool:
        return p1[0] // 3 == p2[0] // 3 and p1[1] // 3 == p2[1] // 3


class SudokuRule(GlobalRule):

    def __init__(self):
        self.sub_rules: list[Rule] = [ColumnRule(), RowRule(), BoxRule()]

    def conflict(self, p1: tuple[int, int], p2: tuple[int, int]) -> bool:
        return self.sub_rules[0].conflict(p1, p2) or \
               self.sub_rules[1].conflict(p1, p2) or \
               self.sub_rules[2].conflict(p1, p2)
