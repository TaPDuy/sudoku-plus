from .board import Board


class Rule:

    def __init__(self):
        self.conflicts: dict[tuple, set] = {}
        self.value_to_tile_map: dict[int, set] = {}
        self.board = None

    def update(self, pos: tuple[int, int], new_val: int, old_val: int):
        pass

    def _check_conflict(self, pos: tuple[int, int], new_val: int, old_val: int):
        if old_val:
            if self.conflicts.get(pos):
                for conflict in self.conflicts.get(pos):
                    self.conflicts[conflict].remove(pos)

                    if not len(self.conflicts[conflict]):
                        self.conflicts.pop(conflict)

                self.conflicts.pop(pos)

            self.value_to_tile_map[old_val].remove(pos)

        if new_val:
            if not self.value_to_tile_map.get(new_val):
                self.value_to_tile_map[new_val] = set()

            for valpos in self.value_to_tile_map[new_val]:
                if self._conflict(valpos, pos):
                    if not self.conflicts.get(pos):
                        self.conflicts[pos] = set()
                    if not self.conflicts.get(valpos):
                        self.conflicts[valpos] = set()

                    self.conflicts[pos].add(valpos)
                    self.conflicts[valpos].add(pos)

            self.value_to_tile_map[new_val].add(pos)

    def _conflict(self, p1: tuple[int, int], p2: tuple[int, int]) -> bool:
        """Describes how two positions would conflict for this rule."""
        return False

    def check(self) -> bool:
        return True


class RuleManager:

    def __init__(self, board: Board, rules: list[Rule] = None):
        self.rules: list[Rule] = rules or list()

        self.component_rules = []
        self.global_rules = []
        self.pos_to_comp_map: dict[tuple, set] = {}

        for rule in self.rules:
            if isinstance(rule, ComponentRule):
                self.component_rules.append(rule)
                for pos in rule.bound_to:
                    if not self.pos_to_comp_map.get(pos):
                        self.pos_to_comp_map[pos] = set()
                    self.pos_to_comp_map[pos].add(rule)
            else:
                self.global_rules.append(rule)
            rule.board = board

    def update(self, pos: tuple[int, int], new_val: int, old_val: int):
        for rule in self.global_rules:
            rule.update(pos, new_val, old_val)

        if self.pos_to_comp_map.get(pos):
            for rule in self.pos_to_comp_map[pos]:
                rule.update(pos, new_val, old_val)

    def get_conflicts(self) -> set:
        conflicts = set()
        for rule in self.rules:
            conflicts |= rule.conflicts.keys()
        return conflicts

    def check(self) -> bool:
        return all(map(lambda rule: rule.check(), self.rules))


class GlobalRule(Rule):

    def update(self, pos: tuple[int, int], new_val: int, old_val: int):
        super()._check_conflict(pos, new_val, old_val)

    def check(self) -> bool:
        return len(self.conflicts) == 0


class ComponentRule(Rule):

    def __init__(self, bound_to: list):
        super().__init__()
        self.bound_to = bound_to

    def _conflict(self, p1: tuple[int, int], p2: tuple[int, int]) -> bool:
        return p1 in self.bound_to and p2 in self.bound_to


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
        self.sub_rules: list[Rule] = [ColumnRule(), RowRule(), BoxRule()]

    def _conflict(self, p1: tuple[int, int], p2: tuple[int, int]) -> bool:
        return self.sub_rules[0]._conflict(p1, p2) or \
               self.sub_rules[1]._conflict(p1, p2) or \
               self.sub_rules[2]._conflict(p1, p2)


class KillerRule(ComponentRule):

    def __init__(self, target_sum: int, bound_to: list):
        super().__init__(bound_to)

        self.sum = 0
        self.target = target_sum

    def update(self, pos: tuple[int, int], new_val: int, old_val: int):
        super()._check_conflict(pos, new_val, old_val)
        self.sum = self.sum - old_val + new_val

    def check(self) -> bool:
        return self.sum == self.target
