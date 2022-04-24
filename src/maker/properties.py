from enum import Enum
import re

from pygame.rect import Rect
from pygame_gui.elements import UITextEntryLine, UIPanel, UILabel
from pygame_gui.core.interfaces import IUIManagerInterface

from core.exception import PropertiesError


class PropertiesType(Enum):
    INT = 0
    INT_LIST = 1
    POS = 2
    POS_LIST = 3


class Properties:
    def __init__(self, name: str, data_type: PropertiesType, data):
        self.data = data
        self.type = data_type
        self.name = name


class PropertiesInput(UIPanel):
    def __init__(self, rect: Rect, manager: IUIManagerInterface, container=None, label: str = "", type: PropertiesType=PropertiesType.INT):
        super().__init__(rect, 0, manager, container=container)
        self.type = type
        self.label = UILabel(Rect(0, 0, rect.w, 30), label, self.ui_manager, self)
        self.input = UITextEntryLine(Rect(0, 20, rect.w, 30), self.ui_manager, self)

    def set_text(self, text: str):
        self.input.set_text(text)

    def get_text(self) -> str:
        return self.input.get_text()

    def set_data(self, data):
        pass

    def get_data(self) -> tuple | int:
        if not self.validate():
            raise PropertiesError("Invalid inputs!")
        return self.process_input(self.input.get_text())

    def validate(self) -> bool:
        pattern = re.compile(r"^((\((\d+(,\s*)*)+\)|\d+)(,\s*)*)+$")
        return bool(re.match(pattern, self.input.get_text()))

    def process_input(self, input_str: str) -> tuple | int:
        if input_str.isnumeric():
            return int(input_str)
        if re.match(r"^\([^()]+\)$", input_str):
            return tuple(int(_.group()) for _ in re.finditer(r"\d+", input_str)),
        return self.__process_input_recursive(input_str)

    def __process_input_recursive(self, input_str: str) -> tuple | int:
        if input_str.isnumeric():
            return int(input_str)
        if re.fullmatch(r"^\([^()]+\)$", input_str):
            input_str = input_str[1:-1]

        splits_pat = re.compile(r"\((\d+(,\s*)*)+\)|\d+")
        splits = re.finditer(splits_pat, input_str)
        return tuple(self.__process_input_recursive(_.group()) for _ in splits)
