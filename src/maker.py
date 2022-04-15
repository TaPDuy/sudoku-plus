from . import Application
from .makerui import PropertiesPanel
from .sudoku.rules import KillerRule

import pygame as pg
import pygame_gui as pgui
from pygame.rect import Rect, RectType
from pygame_gui.elements import UIPanel, UISelectionList, UIDropDownMenu, UIButton, UITextEntryLine


class LevelMaker(Application):

    def __init__(self):
        super().__init__((1080, 720))

        self.rule_panel = UIPanel(Rect(10, 10, 300, 600), 0, self.ui_manager)
        self.rule_drop_down = UIDropDownMenu([
            "Sudoku",
            "Column",
            "Row",
            "Box",
            "Diagonal",
            "Main Diagonal",
            "Anti Diagonal",
            "Knight",
            "King",
            "Killer",
            "Arrow",
            "Thermometer",
            "Palindrome",
            "Even",
            "Odd",
            "Black dot",
            "White dot",
            "Surround"
        ], "Sudoku", Rect(10, 10, 150, 20), self.ui_manager, container=self.rule_panel)
        self.add_button = UIButton(
            Rect(self.rule_drop_down.relative_rect.topright, (20, 20)), "+",
            self.ui_manager, container=self.rule_panel
        )
        self.rule_list = UISelectionList(Rect(10, 40, 150, 100), [], self.ui_manager, container=self.rule_panel)
        self.selected_rules = []

        self.properties_panel = PropertiesPanel(Rect(0, 200, 200, 300), self.ui_manager, self.rule_panel)
        self.properties_panel.set_rule(KillerRule(20, {(2, 3), (3, 4)}))

    def _process_events(self, evt):
        match evt.type:
            case pg.WINDOWCLOSE:
                self.close()
            case pgui.UI_BUTTON_PRESSED:
                if evt.ui_element == self.add_button:
                    self.selected_rules.append(self.rule_drop_down.selected_option)
                    self.rule_list.set_item_list(self.selected_rules)
            case pgui.UI_SELECTION_LIST_NEW_SELECTION:
                print(self.rule_list.get_single_selection())

    def _update(self, dt):
        pass

    def _draw(self, surface) -> list[Rect | RectType]:
        return list()
