class Rule:
    pass


class GlobalRule(Rule):
    pass


class ComponentRule(Rule):
    pass


class ColumnRule(GlobalRule):

    @staticmethod
    def conflict(p1: tuple[int, int], p2: tuple[int, int]) -> bool:
        return p1[0] == p2[0]
