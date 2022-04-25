from pygame import Surface
from src.sudoku.board import Board
from src.maker.properties import Properties


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
        """Describes how two positions would conflict for this rules."""
        return False

    def check(self) -> bool:
        return True


class RuleManager:

    def __init__(self, board: Board, rules: set[Rule] = None):
        self.board = board

        self.component_rules = set()
        self.global_rules = set()
        self.pos_to_comp_map: dict[tuple, set] = {}

        self.rules: set[Rule] = set()
        if rules:
            self.add_rule(rules)

    def add_rule(self, rules: set[Rule]):
        for rule in rules:
            if isinstance(rule, ComponentRule):
                self.component_rules.add(rule)
                for pos in rule.bound_to:
                    if not self.pos_to_comp_map.get(pos):
                        self.pos_to_comp_map[pos] = set()
                    self.pos_to_comp_map[pos].add(rule)
            elif isinstance(rule, GlobalRule):
                self.global_rules.add(rule)
            rule.board = self.board

        self.rules = self.component_rules | self.global_rules

    def clear_rule(self):
        self.rules = set()
        self.component_rules = set()
        self.global_rules = set()
        self.pos_to_comp_map: dict[tuple, set] = {}

    def update(self, new_val: int, old_values: dict[tuple[int, int], int]):
        for pos, old_val in old_values.items():
            for rule in self.global_rules:
                rule.update(pos, 0 if new_val == old_val else new_val, old_val)

            if self.pos_to_comp_map.get(pos):
                for rule in self.pos_to_comp_map[pos]:
                    rule.update(pos, 0 if new_val == old_val else new_val, old_val)

        self.board.highlight_conflicts(self.get_conflicts())

    def get_conflicts(self) -> set:
        conflicts = set()
        for rule in self.rules:
            conflicts |= rule.conflicts.keys()
        return conflicts

    def check(self) -> bool:
        return all(map(lambda rule: rule.check(), self.rules)) and self.board.is_complete()


class GlobalRule(Rule):

    def update(self, pos: tuple[int, int], new_val: int, old_val: int):
        super()._check_conflict(pos, new_val, old_val)

    def check(self) -> bool:
        return len(self.conflicts) == 0


class ComponentRule(Rule):

    def __init__(self, bound_to):
        super().__init__()
        self.bound_to = bound_to

    def _conflict(self, p1: tuple[int, int], p2: tuple[int, int]) -> bool:
        return p1 in self.bound_to and p2 in self.bound_to

    def draw(self, surface: Surface):
        pass

    def get_properties(self) -> list[Properties]:
        return []

    def set_properties(self, *data):
        pass
