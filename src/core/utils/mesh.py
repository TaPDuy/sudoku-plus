from abc import abstractmethod, ABC


class MeshGrid(ABC):
    """Holds and calculates the data needed to build a mesh base using Marching Square."""

    def __init__(self, size: tuple[int, int]):
        """state_size: The size of the state grid
        bit_size: the size of the bit grid"""

        self.state_size = self.state_w, self.state_h = size
        self.bit_size = self.bit_w, self.bit_h = self.state_w + 1, self.state_h + 1

        self._states = [[0 for _ in range(self.state_w)] for _ in range(self.state_h)]
        self.bits = [[0 for _ in range(self.bit_w)] for _ in range(self.bit_h)]

    @property
    def states(self):
        return self._states

    def reset(self):
        self._states = [[0 for _ in range(self.state_w)] for _ in range(self.state_h)]
        self.bits = [[0 for _ in range(self.bit_w)] for _ in range(self.bit_h)]

    def add(self, value: int, bit_pos: set[tuple[int, int]]) -> set[tuple[int, int]]:
        """Adds value to specified positions"""
        # Update bits and record affected states
        affected = set()
        for bx, by in bit_pos:
            self.bits[by][bx] += value
            affected |= self.bit_to_state(bx, by)

        # Update affected states
        for sx, sy in affected:
            self.update_state(sx, sy)

        return affected

    @abstractmethod
    def bit_to_state(self, bx, by) -> set[tuple[int, int]]:
        """Describes how bit position map to state position"""
        return set()

    @abstractmethod
    def update_state(self, sx, sy):
        """Recalculates the specified state position"""
        pass
