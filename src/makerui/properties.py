import re

from pygame import Rect
import pygame_gui as pgui
from pygame_gui.elements import UIPanel, UILabel, UITextEntryLine, UIButton, UITextBox
from pygame_gui.core.interfaces import IUIManagerInterface

from src.sudoku.rules import ComponentRule
from src.core import Event, PropertiesError


class PropertiesPanel(UIPanel):

    def __init__(self, relative_rect: Rect, manager: IUIManagerInterface, container=None):
        super().__init__(relative_rect, 0, manager, container=container)
        self.current_rule = None
        self.apply_btn = UIButton(Rect(0, 0, 100, 30), "Apply", self.ui_manager, self)

        self.message = ""
        self.message_board = UITextBox(f"<p>{self.message}</p>", Rect(0, 0, 200, 100), self.ui_manager, container=self)

        self.labels = {}
        self.inputs = {}

        # Events
        self.on_applied = Event()

    def set_rule(self, rule: ComponentRule):
        self.current_rule = rule

        for _ in self.labels.values():
            _.kill()
        self.labels = {}

        for _ in self.inputs.values():
            _.kill()
        self.inputs = {}

        i = 0
        for property_id, name in rule.get_properties().items():
            self.labels[property_id] = UILabel(Rect(0, i * 60, 200, 30), name, self.ui_manager, self)
            self.inputs[property_id] = UITextEntryLine(Rect(0, i * 60 + 20, 200, 30), self.ui_manager, self)
            self.inputs[property_id].set_text(rule.get_properties_value_string(property_id))
            i += 1

        self.apply_btn.set_relative_position((0, i * 60))
        self.message_board.set_relative_position((0, i * 60 + 30))

    def validate(self) -> bool:
        pattern = re.compile(r"^((\((\d+(,\s*)*)+\)|\d+)(,\s*)*)+$")
        for _in in self.inputs.values():
            if not re.match(pattern, _in.get_text()):
                return False
        return True

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

    def process_event(self, evt):
        match evt.type:
            case pgui.UI_BUTTON_PRESSED:
                if evt.ui_element is self.apply_btn:
                    if self.validate():
                        data = (self.process_input(_in.get_text()) for _in in self.inputs.values())
                        try:
                            self.current_rule.set_properties(*data)
                        except PropertiesError as e:
                            self.message_board.set_text(str(e))
                        else:
                            self.message_board.set_text("Updated rule successfully!")
                            self.on_applied()
                    else:
                        pass
