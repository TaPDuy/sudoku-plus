from pygame import Rect
import pygame_gui as pgui
from pygame_gui.elements import UIPanel, UIButton, UITextBox
from pygame_gui.core.interfaces import IUIManagerInterface

from sudoku.rules.rule import ComponentRule
from core.event import Event
from core.exception import PropertiesError
from maker.properties import PropertiesInput


class PropertiesPanel(UIPanel):

    def __init__(self, relative_rect: Rect, manager: IUIManagerInterface, container=None):
        super().__init__(relative_rect, 0, manager, container=container)
        self.current_rule = None
        self.apply_btn = UIButton(Rect(0, 0, 100, 30), "Apply", self.ui_manager, self)

        self.message = ""
        self.message_board = UITextBox(f"<p>{self.message}</p>", Rect(0, 0, 200, 100), self.ui_manager, container=self)

        self.inputs = []

        # Events
        self.on_applied = Event()

    def set_rule(self, rule):
        if not isinstance(rule, ComponentRule):
            self.message_board.set_text("Global rules have no properties.")
            return

        self.current_rule = rule

        for _ in self.inputs:
            _.kill()
        self.inputs = []

        i = 0
        for properties in rule.get_properties():
            _input = PropertiesInput(
                Rect(0, i * 60, 200, 60), self.ui_manager, self,
                label=properties.name, type=properties.type
            )
            _input.set_data(properties.data)
            self.inputs.append(_input)
            i += 1

        self.apply_btn.set_relative_position((0, i * 60))
        self.message_board.set_relative_position((0, i * 60 + 30))

    def process_event(self, evt):
        match evt.type:
            case pgui.UI_BUTTON_PRESSED:
                if evt.ui_element is self.apply_btn:
                    try:
                        data = (_in.get_data() for _in in self.inputs)
                        self.current_rule.set_properties(*data)
                    except PropertiesError as e:
                        self.message_board.set_text(str(e))
                    else:
                        self.message_board.set_text("Updated rule successfully!")
                        self.on_applied()
