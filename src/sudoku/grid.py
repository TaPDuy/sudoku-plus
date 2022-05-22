from enum import Enum

from core.action import new_action, Action
from core.event import Event


class InputMode(Enum):
    INPUT_MODE_VALUE = 0
    INPUT_MODE_MARK = 1
    INPUT_MODE_COLOR = 2


class Tile:

    def __init__(self):

        self.color = 0
        self.value = 0
        self.mark = 0
        self.locked = False
        self.highlight = False


class BoardInputAction(Action):

    def __init__(self, **data):
        super().__init__(**data)
        self.grid = data['component']
        self.mode = data['input_mode']
        self.old_values = data['old_values']
        self.value = data['new_value']

    def redo(self):
        for pos in self.old_values.keys():
            match self.mode:
                case InputMode.INPUT_MODE_VALUE:
                    self.grid.set_value(pos, self.value)
                case InputMode.INPUT_MODE_MARK:
                    self.grid.set_mark(pos, self.value)
                case InputMode.INPUT_MODE_COLOR:
                    self.grid.set_color(pos, self.value)

    def undo(self):
        for pos, old in self.old_values.items():
            match self.mode:
                case InputMode.INPUT_MODE_VALUE:
                    self.grid.set_value(pos, old)
                case InputMode.INPUT_MODE_MARK:
                    self.grid.set_mark(pos, old)
                case InputMode.INPUT_MODE_COLOR:
                    self.grid.set_color(pos, old)


class Grid:

    def __init__(self):
        # Properties
        self.tlsize = self.tlw, self.tlh = 9, 9

        # Control properties
        self.__tile_filled = 0

        # Components
        self.tiles = [[Tile() for x in range(self.tlw)] for y in range(self.tlh)]

        # Events
        self.on_changed = Event()

    def set_value(self, pos: tuple[int, int], value: int, lock=False):
        tile = self.tiles[pos[1]][pos[0]]
        old_value = tile.value

        if not tile.locked:
            if lock:
                tile.locked = True

            tile.value = 0 if value == old_value else value
            self.__tile_filled += bool(tile.value) - bool(old_value)
            self.on_changed(new_val=value, old_values={pos: old_value}, positions={pos})

        return old_value

    def set_mark(self, pos: tuple[int, int], value: int):
        tile = self.tiles[pos[1]][pos[0]]
        old_value = tile.mark
        tile.mark = value

        self.on_changed(positions={pos})
        return old_value

    def toggle_mark(self, pos: tuple[int, int], value: int):
        tile = self.tiles[pos[1]][pos[0]]
        return self.set_mark(pos, tile.mark ^ 1 << (value - 1) if value else 0)

    def set_color(self, pos: tuple[int, int], value: int):
        tile = self.tiles[pos[1]][pos[0]]
        old_value = tile.color
        tile.color = 0 if value == old_value else value

        self.on_changed(positions={pos})
        return old_value

    @new_action(BoardInputAction)
    def fill_tiles(self, value: int, mode: InputMode, tiles: list | set, **kwargs):
        old_values = {}
        for pos in tiles:
            match mode:
                case InputMode.INPUT_MODE_VALUE:
                    old_values[pos] = self.set_value(pos, value, **kwargs)
                case InputMode.INPUT_MODE_MARK:
                    old_values[pos] = self.toggle_mark(pos, value)
                case InputMode.INPUT_MODE_COLOR:
                    old_values[pos] = self.set_color(pos, value)

        return {'component': self, 'input_mode': mode, 'old_values': old_values, 'new_value': value}

    def get_numbered_tiles(self) -> dict[tuple[int, int], int]:
        return {(x, y): self.tiles[y][x].value for y in range(self.tlh) for x in range(self.tlw) if self.tiles[y][x].value}

    def is_complete(self) -> bool:
        print(self.__tile_filled)
        return self.__tile_filled == self.tlw * self.tlh

    def clear(self):
        self.__tile_filled = 0
        for y in range(self.tlh):
            for x in range(self.tlw):
                self.tiles[y][x].value = 0
                self.tiles[y][x].mark = 0
                self.tiles[y][x].color = 0
                self.tiles[y][x].locked = False

        self.on_changed(positions={(x, y) for y in range(self.tlh) for x in range(self.tlw)})

    def highlight_conflicts(self, conflicts: set, old_conflicts: set):
        changed_conflicts = conflicts.difference(old_conflicts)
        changed_nonconflicts = old_conflicts.difference(conflicts)

        for cx, cy in changed_nonconflicts:
            self.tiles[cy][cx].highlight = False
        for cx, cy in changed_conflicts:
            self.tiles[cy][cx].highlight = True

        self.on_changed(positions=changed_conflicts | changed_nonconflicts)
