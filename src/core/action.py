from abc import ABC, abstractmethod


from ..sudoku.board import Board, InputMode


class Action(ABC):

    @abstractmethod
    def undo(self):
        pass

    @abstractmethod
    def __call__(self):
        pass


class ActionManager:

    def __init__(self):
        self.undo_stack = []
        self.redo_stack = []

    def new_action(self, action):
        self.undo_stack.append(action)
        self.redo_stack.clear()

    def push_undo(self, action: Action):
        self.undo_stack.append(action)

    def push_redo(self, action: Action):
        self.redo_stack.append(action)

    def pop_undo(self) -> Action:
        undo = None
        try:
            undo = self.undo_stack.pop()
        except IndexError:
            print("Nothing to undo!")
        finally:
            return undo

    def pop_redo(self) -> Action:
        redo = None
        try:
            redo = self.redo_stack.pop()
        except IndexError:
            print("Nothing to redo!")
        finally:
            return redo

    def undo(self):
        action = self.pop_undo()
        if action:
            action.undo()
            self.push_redo(action)

    def redo(self):
        action = self.pop_redo()
        if action:
            action()
            self.push_undo(action)


class BoardInputAction(Action):

    def __init__(
        self,
        board: Board,
        value: int,
        mode: InputMode,
        old_values: dict[tuple[int, int], int]
    ):
        self.board = board
        self.mode = mode
        self.old_values = old_values
        self.value = value

    def __repr__(self):
        return f"[prev={self.old_values}, value={self.value}, mode={self.mode}]"

    def __call__(self):
        self.board.fill_tiles(self.value, self.mode, self.old_values.keys())

    def undo(self):
        for tile, val in self.old_values.items():
            self.board.fill_tile(val, self.mode, tile)
