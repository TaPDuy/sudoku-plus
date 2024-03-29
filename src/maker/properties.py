from enum import Enum
import re

from pygame.rect import Rect
from pygame_gui.elements import UITextEntryLine, UIPanel, UILabel
from pygame_gui.core.interfaces import IUIManagerInterface


class PropertiesType(Enum):
    INT = 0
    INT_LIST = 1
    POS = 2
    POS_LIST = 3


class PropertiesError(Exception):
    """Raised when the edited rule invalidates the entered properties."""
    pass


class Properties:
    def __init__(self, name: str, data_type: PropertiesType, data):
        self.data = data
        self.type = data_type
        self.name = name


POS_REGEX = r"\(\s*\d+\s*,\s*\d+\s*\)"
INT_LIST_PATTERN = re.compile(r"^(\d+\s*,\s*)*\d+$")
POS_PATTERN = re.compile(fr"^{POS_REGEX}$")
POS_LIST_PATTERN = re.compile(fr"^(({POS_REGEX})\s*,\s*)*({POS_REGEX})$")


class PropertiesInput(UIPanel):
    def __init__(
            self, rect: Rect,
            manager: IUIManagerInterface,
            container=None, label: str = "",
            property_type: PropertiesType = PropertiesType.INT
    ):
        super().__init__(rect, 0, manager, container=container, margins={'left': 0, 'right': 0, 'top': 0, 'bottom': 0})
        self.type = property_type

        self.pad = 10
        self.label = UILabel(Rect(
            0, self.pad, self.relative_rect.w, self.relative_rect.h / 2 - self.pad
        ), label, self.ui_manager, self)
        self.input = UITextEntryLine(Rect(
            self.pad, self.label.relative_rect.bottom,
            self.relative_rect.w - 2 * self.pad, self.relative_rect.h / 2
        ), self.ui_manager, self)

    def set_relative_rect(self, rect: Rect):
        self.label.set_relative_position((0, self.pad))
        self.label.set_dimensions((rect.w, rect.h / 2 - self.pad))

        self.input.set_relative_position((self.pad, self.label.relative_rect.bottom))
        self.input.set_dimensions((rect.w - 2 * self.pad, rect.h / 2))

        self.set_relative_position(rect.topleft)
        self.set_dimensions(rect.size)

    def set_text(self, text: str):
        self.input.set_text(text)

    def get_text(self) -> str:
        return self.input.get_text()

    def set_data(self, data):
        data_str = ""
        match self.type:
            case PropertiesType.INT | PropertiesType.POS:
                data_str = str(data)
            case PropertiesType.INT_LIST | PropertiesType.POS_LIST:
                data_str = ", ".join(str(_) for _ in data)
        self.set_text(data_str)

    def get_data(self) -> tuple | int:
        input_str = self.input.get_text().strip()

        # Validate
        match self.type:
            case PropertiesType.INT:
                if not input_str.isnumeric():
                    raise PropertiesError(f"{self.label.text} should be integer.")
            case PropertiesType.INT_LIST:
                if not re.match(INT_LIST_PATTERN, input_str):
                    raise PropertiesError(f"{self.label.text} should be a list of integers.")
            case PropertiesType.POS:
                if not re.match(POS_PATTERN, input_str):
                    raise PropertiesError(f"{self.label.text} should be a 2D position.")
            case PropertiesType.POS_LIST:
                if not re.match(POS_LIST_PATTERN, input_str):
                    raise PropertiesError(f"{self.label.text} should be a list of 2D positions.")

        return self.process_input(self.input.get_text())

    def process_input(self, input_str: str) -> tuple | int:
        if self.type == PropertiesType.INT:
            return int(input_str)
        else:
            splits = re.findall(r"\d+", input_str)
            if self.type == PropertiesType.POS_LIST:
                return tuple((int(splits[i]), int(splits[i + 1])) for i in range(0, len(splits), 2))
            else:
                return tuple(int(num) for num in splits)
