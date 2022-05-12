import pygame_gui as pgui
from pygame import Rect
from pygame_gui.core.interfaces import IUIManagerInterface
from pygame_gui.elements import UIPanel, UIDropDownMenu, UIButton, UISelectionList, UILabel

from bidict import bidict

from sudoku.rules import (
    SudokuRule, ColumnRule, RowRule, BoxRule,
    DiagonalRule, MainDiagonalRule, AntiDiagonalRule,
    KnightRule, KingRule, KillerRule, ArrowRule,
    ThermometerRule, PalindromeRule,
    EvenRule, OddRule, BlackDotRule, WhiteDotRule, SurroundRule, GlobalRule
)
from core.event import Event


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
        super().__init__(
            relative_rect, 0, manager, container=container,
            margins={'left': 0, 'right': 0, 'top': 0, 'bottom': 0}
        )

        self.selected_rules = []

        self.pad = 10
        self.label_w, self.label_h = self.relative_rect.w, 20
        self.btn_w, self.btn_h = (self.relative_rect.w - 3 * self.pad) / 2, 30
        self.max_list_height = 300

        self.label_1 = UILabel(Rect(0, self.pad, self.label_w, self.label_h), "Select rule", manager, self)
        self.rule_drop_down = UIDropDownMenu(list(RuleListPanel.__RULE_CLASSES.keys()), "Sudoku", Rect(
            self.pad, self.label_1.relative_rect.bottom + self.pad,
            self.relative_rect.w - 2 * self.pad, self.label_h
        ), self.ui_manager, self)

        self.add_button = UIButton(Rect(
            self.pad, self.rule_drop_down.relative_rect.bottom + self.pad,
            self.btn_w, self.btn_h
        ), "Add", self.ui_manager, self)
        self.remove_button = UIButton(Rect(
            self.btn_w + 2 * self.pad, self.rule_drop_down.relative_rect.bottom + self.pad,
            self.btn_w, self.btn_h
        ), "Remove", self.ui_manager, self)

        self.label_2 = UILabel(Rect(
            0, self.add_button.relative_rect.bottom + self.pad,
            self.label_w, self.label_h
        ), "Rule list", manager, self)

        self.rule_list = UISelectionList(Rect(
            self.pad, self.label_2.relative_rect.bottom + self.pad,
            self.relative_rect.w - 2 * self.pad,
            min(self.max_list_height, self.relative_rect.height - self.label_2.relative_rect.bottom - 2 * self.pad)
        ), [], self.ui_manager, container=self)

        # Events
        self.on_rule_selected = Event()
        self.on_rule_added = Event()
        self.on_rule_removed = Event()

    def set_rule_list(self, rules: set):
        self.selected_rules = list(rules)
        self.rule_list.set_item_list([RuleListPanel.__RULE_CLASSES.inverse[type(rule)] for rule in self.selected_rules])

    def process_event(self, evt):
        match evt.type:
            case pgui.UI_BUTTON_PRESSED:
                if evt.ui_element == self.add_button:
                    select = self.rule_drop_down.selected_option
                    existed = issubclass(RuleListPanel.__RULE_CLASSES[select], GlobalRule) and select in [
                        RuleListPanel.__RULE_CLASSES.inverse[type(rule)] for rule in self.selected_rules
                    ]

                    if not existed:
                        rule = RuleListPanel.__RULE_CLASSES[select]()
                        self.selected_rules.append(rule)
                        self.on_rule_added(rules=rule)
                        self.rule_list.set_item_list([
                            RuleListPanel.__RULE_CLASSES.inverse[type(rule)] for rule in self.selected_rules
                        ])
                if evt.ui_element == self.remove_button:
                    index = -1
                    for item in self.rule_list.item_list:
                        if item['selected']:
                            index = self.rule_list.item_list.index(item)
                            break

                    self.on_rule_removed(rules=self.selected_rules.pop(index))
                    self.rule_list.set_item_list([RuleListPanel.__RULE_CLASSES.inverse[type(rule)] for rule in self.selected_rules])

            case pgui.UI_SELECTION_LIST_NEW_SELECTION:
                if evt.ui_element == self.rule_list:
                    index = -1
                    for item in self.rule_list.item_list:
                        if item['selected']:
                            index = self.rule_list.item_list.index(item)
                            break

                    if index != -1:
                        self.on_rule_selected(rule=self.selected_rules[index])
