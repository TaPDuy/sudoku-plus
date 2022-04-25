import pygame_gui as pgui
from pygame import Rect
from pygame_gui.core.interfaces import IUIManagerInterface
from pygame_gui.elements import UIPanel, UIDropDownMenu, UIButton, UISelectionList

from bidict import bidict

from sudoku.rules import (
    SudokuRule, ColumnRule, RowRule, BoxRule,
    DiagonalRule, MainDiagonalRule, AntiDiagonalRule,
    KnightRule, KingRule, KillerRule, ArrowRule,
    ThermometerRule, PalindromeRule,
    EvenRule, OddRule, BlackDotRule, WhiteDotRule, SurroundRule
)
from core.event import Event, EventData


class RuleListPanel(UIPanel):
    __RULE_CLASSES = bidict({
        "Sudoku": SudokuRule, "Column": ColumnRule, "Row": RowRule, "Box": BoxRule,
        "Diagonal": DiagonalRule, "Main Diagonal": MainDiagonalRule, "Anti Diagonal": AntiDiagonalRule,
        "Knight": KnightRule, "King": KingRule, "Killer": KillerRule, "Arrow": ArrowRule,
        "Thermometer": ThermometerRule, "Palindrome": PalindromeRule,
        "Even": EvenRule, "Odd": OddRule,
        "Black dot": BlackDotRule, "White dot": WhiteDotRule, "Surround": SurroundRule
    })

    def __init__(self, relative_rect: Rect, manager: IUIManagerInterface, container=None):
        super().__init__(relative_rect, 0, manager, container=container)
        self.rule_drop_down = UIDropDownMenu(
            list(RuleListPanel.__RULE_CLASSES.keys()), "Sudoku",
            Rect(10, 10, 150, 20), self.ui_manager, container=self
        )
        self.add_button = UIButton(
            Rect(self.rule_drop_down.relative_rect.topright, (20, 20)), "+",
            self.ui_manager, container=self
        )
        self.rule_list = UISelectionList(Rect(10, 40, 150, 100), [], self.ui_manager, container=self)
        self.selected_rules = []

        # Events
        self.on_rule_selected = Event()

    def set_rule_list(self, rules: set):
        self.selected_rules = list(rules)
        self.rule_list.set_item_list([RuleListPanel.__RULE_CLASSES.inverse[type(rule)] for rule in self.selected_rules])

    def process_event(self, evt):
        match evt.type:
            case pgui.UI_BUTTON_PRESSED:
                if evt.ui_element == self.add_button:
                    self.selected_rules.append(RuleListPanel.__RULE_CLASSES[self.rule_drop_down.selected_option]())
                    self.rule_list.set_item_list([RuleListPanel.__RULE_CLASSES.inverse[type(rule)] for rule in self.selected_rules])
            case pgui.UI_SELECTION_LIST_NEW_SELECTION:
                index = -1
                for item in self.rule_list.item_list:
                    if item['selected']:
                        index = self.rule_list.item_list.index(item)
                        break

                if index != -1:
                    self.on_rule_selected(EventData({'rule': self.selected_rules[index]}))
