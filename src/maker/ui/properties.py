from pygame import Rect
import pygame_gui as pgui
from pygame_gui.elements import UIPanel, UIButton, UITextBox
from pygame_gui.core.interfaces import IUIManagerInterface

from sudoku.rules.rule import ComponentRule
from core.event import Event
from maker.properties import PropertiesInput, PropertiesError


class PropertiesPanel(UIPanel):

    def __init__(self, relative_rect: Rect, manager: IUIManagerInterface, container=None):
        super().__init__(
            relative_rect, 0, manager, container=container,
            margins={'left': 0, 'right': 0, 'top': 0, 'bottom': 0}
        )

        self.current_rule = None
        self.message = ""
        self.inputs = []

        self.pad = 10
        self.input_height = 60
        self.label_w, self.label_h = self.relative_rect.w, 20
        self.max_msg_height = 500

        self.apply_btn = UIButton(Rect(
            self.pad, self.pad, self.relative_rect.w - 2 * self.pad, 30
        ), "Apply", self.ui_manager, self)

        self.message_board = UITextBox(
            f"<p>{self.message}</p>",
            Rect(
                self.pad, self.apply_btn.relative_rect.bottom + self.pad,
                self.relative_rect.w - 2 * self.pad,
                min(
                    self.max_msg_height,
                    self.relative_rect.height - self.apply_btn.relative_rect.bottom - 2 * self.pad
                )
            ),
            self.ui_manager, container=self
        )

        # Events
        self.on_applied = Event()

    def set_rule(self, rule):
        for _ in self.inputs:
            _.kill()
        self.inputs = []

        self.current_rule = rule
        if not self.current_rule:
            self.apply_btn.hide()
            self.message_board.set_text("")
            return

        i = 0
        if not isinstance(rule, ComponentRule):
            self.message_board.set_text("Global rules have no properties.")
            self.apply_btn.hide()
        else:
            for properties in rule.get_properties():
                _input = PropertiesInput(
                    Rect(
                        0, i * self.input_height,
                        self.relative_rect.w, self.input_height
                    ),
                    self.ui_manager, self,
                    label=properties.name, property_type=properties.type
                )
                _input.set_data(properties.data)
                self.inputs.append(_input)
                i += 1
            self.apply_btn.show()

        self.apply_btn.set_relative_position((self.pad, i * self.input_height + self.pad))
        self.message_board.set_relative_position((
            self.pad, self.apply_btn.relative_rect.bottom + self.pad
        ))
        self.message_board.set_dimensions((self.message_board.relative_rect.w, min(
            self.max_msg_height,
            self.relative_rect.height - self.apply_btn.relative_rect.bottom - 2 * self.pad
        )))

    def set_relative_rect(self, rect: Rect):
        self.label_w, self.label_h = rect.w, 20

        # self.apply_btn.set_relative_position((self.pad, self.pad))
        # self.apply_btn.set_dimensions((rect.w - 2 * self.pad, 30))

        # self.message_board.set_relative_position((self.pad, self.apply_btn.relative_rect.bottom + self.pad))
        # self.message_board.set_dimensions((
        #     rect.w - 2 * self.pad, min(
        #         self.max_msg_height,
        #         rect.h - self.apply_btn.relative_rect.bottom - 2 * self.pad
        #     )
        # ))

        i = 0
        for _ in self.inputs:
            _.set_relative_rect(Rect(0, i * self.input_height, rect.w, self.input_height))
            i += 1

        self.apply_btn.set_relative_position((self.pad, i * self.input_height + self.pad))
        self.apply_btn.set_dimensions((rect.w - 2 * self.pad, 30))
        self.message_board.set_relative_position((
            self.pad, self.apply_btn.relative_rect.bottom + self.pad
        ))
        self.message_board.set_dimensions((rect.w - 2 * self.pad, min(
            self.max_msg_height,
            rect.h - self.apply_btn.relative_rect.bottom - 2 * self.pad
        )))

        self.set_relative_position(rect.topleft)
        self.set_dimensions(rect.size)

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
