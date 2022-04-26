from sudoku.rules.rule import GlobalRule


class ColumnRule(GlobalRule):

    def _conflict(self, p1: tuple[int, int], p2: tuple[int, int]) -> bool:
        return p1[0] == p2[0]


class RowRule(GlobalRule):

    def _conflict(self, p1: tuple[int, int], p2: tuple[int, int]) -> bool:
        return p1[1] == p2[1]


class BoxRule(GlobalRule):

    def _conflict(self, p1: tuple[int, int], p2: tuple[int, int]) -> bool:
        return p1[0] // 3 == p2[0] // 3 and p1[1] // 3 == p2[1] // 3


class SudokuRule(GlobalRule):

    def __init__(self):
        super().__init__()
        self.sub_rules: list[GlobalRule] = [ColumnRule(), RowRule(), BoxRule()]

    def _conflict(self, p1: tuple[int, int], p2: tuple[int, int]) -> bool:
        return self.sub_rules[0]._conflict(p1, p2) or \
               self.sub_rules[1]._conflict(p1, p2) or \
               self.sub_rules[2]._conflict(p1, p2)


class MainDiagonalRule(GlobalRule):

    def _conflict(self, p1: tuple[int, int], p2: tuple[int, int]) -> bool:
        return p1[0] == p1[1] and p2[0] == p2[1]


class AntiDiagonalRule(GlobalRule):

    def _conflict(self, p1: tuple[int, int], p2: tuple[int, int]) -> bool:
        return p1[0] + p1[1] == p2[0] + p2[1] == 8


class DiagonalRule(GlobalRule):

    def __init__(self):
        super().__init__()
        self.sub_rules: list[GlobalRule] = [MainDiagonalRule(), AntiDiagonalRule()]

    def _conflict(self, p1: tuple[int, int], p2: tuple[int, int]) -> bool:
        return self.sub_rules[0]._conflict(p1, p2) or self.sub_rules[1]._conflict(p1, p2)


class KnightRule(GlobalRule):

    def _conflict(self, p1: tuple[int, int], p2: tuple[int, int]) -> bool:
        return (p1[0] - p2[0], p1[1] - p2[1]) in (
            (-2, -1), (-1, -2), (1, -2), (2, -1),
            (-2, 1), (-1, 2), (1, 2), (2, 1)
        )


class KingRule(GlobalRule):

    def _conflict(self, p1: tuple[int, int], p2: tuple[int, int]) -> bool:
        return (p1[0] - p2[0], p1[1] - p2[1]) in (
            (-1, -1), (0, -1), (1, -1),
            (-1, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)
        )
