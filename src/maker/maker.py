import os

from core.app import Application
from sudoku.grid import InputMode
from sudoku.level import Level
from .ui.rule_list import RuleListPanel
from .ui.properties import PropertiesPanel
from .ui.menu import Menu
from sudoku.board import Board

import pygame as pg
import pygame_gui as pgui
from pygame.sprite import LayeredDirty
from pygame.rect import Rect, RectType
from pygame_gui.elements import UIPanel, UITextEntryLine, UILabel

import pickle
import tkinter.filedialog


class LevelMaker(Application):

    def __init__(self):
        super().__init__((1080, 720))

        self.opened_level_path = ""
        self.levels_path = os.getcwd() + "/levels"
        if not os.path.exists(self.levels_path):
            os.makedirs(self.levels_path)

        self.sprites = LayeredDirty()

        self.left_panel = None
        self.menu = None
        self.rule_list = None

        self.right_panel = None
        self.name = None
        self.properties_panel = None

        self.board = None
        self.init_components()
        self.assign_event_handlers()

        self.new_level()

    def init_components(self):
        ratio = self.width / self.height
        board_size = self.height if ratio > 5 / 3 else .6 * self.width
        self.board = Board(
            (self.width / 2 - board_size / 2, self.height / 2 - board_size / 2),
            board_size, board_size / 11, self.sprites, self.ui_manager
        )

        self.left_panel = UIPanel(
            Rect(0, 0, board_size / 3, self.height), 0, self.ui_manager,
            margins={'left': 0, 'right': 0, 'top': 0, 'bottom': 0}
        )
        self.menu = Menu(Rect(0, 0, self.left_panel.relative_rect.w, 30), self.ui_manager, self.left_panel)
        self.rule_list = RuleListPanel(Rect(
            self.menu.relative_rect.bottomleft,
            (self.left_panel.relative_rect.w, self.left_panel.relative_rect.h - self.menu.relative_rect.h)
        ), self.ui_manager, self.left_panel)

        self.right_panel = UIPanel(
            Rect(self.width - board_size / 3, 0, board_size / 3, self.height), 0, self.ui_manager,
            margins={'left': 0, 'right': 0, 'top': 0, 'bottom': 0}
        )

        pad = 10
        label_1 = UILabel(
            Rect(0, pad, self.right_panel.relative_rect.w, 20),
            "Level name", self.ui_manager, self.right_panel
        )
        self.name = UITextEntryLine(Rect(
            pad, label_1.relative_rect.bottom + pad,
            self.right_panel.relative_rect.w - 2 * pad, 30
        ), self.ui_manager, self.right_panel)

        label_2 = UILabel(
            Rect(
                0, self.name.relative_rect.bottom + pad,
                self.right_panel.relative_rect.w, 20
            ),
            "Rule properties", self.ui_manager, self.right_panel
        )
        self.properties_panel = PropertiesPanel(Rect(
            0, label_2.relative_rect.bottom,
            self.left_panel.relative_rect.w,
            self.left_panel.relative_rect.h - label_2.relative_rect.bottom
        ), self.ui_manager, self.right_panel)

    def assign_event_handlers(self):
        self.rule_list.on_rule_selected.add_handler(self.properties_panel.set_rule)
        self.rule_list.on_rule_added.add_handler(self.board.rule_manager.add_rule)
        self.rule_list.on_rule_removed.add_handler(self.board.rule_manager.remove_rule)

        self.properties_panel.on_applied.add_handler(self.board.redraw_rules)
        self.board.rule_manager.on_rule_added.add_handler(self.board.redraw_rules)
        self.board.rule_manager.on_rule_removed.add_handler(self.board.redraw_rules)

    def load_level(self, level: Level):
        self.name.set_text(level.name)

        self.board.rule_manager.clear_rule()
        self.board.rule_manager.add_rule(level.ruleset)

        self.properties_panel.set_rule(None)
        self.rule_list.set_rule_list(level.ruleset)

        self.board.grid.clear()
        for pos, val in level.start_values.items():
            self.board.fill_tiles(val, [pos], InputMode.INPUT_MODE_VALUE, lock=True, no_record=True)

        self.board.redraw_rules()

    def new_level(self):
        self.opened_level_path = ""
        self.load_level(Level())

    def save(self):
        data = Level(self.name.get_text(), set(self.rule_list.selected_rules), self.board.grid.get_numbered_tiles())
        if not self.opened_level_path:
            path = tkinter.filedialog.asksaveasfilename(
                initialdir=self.levels_path,
                initialfile='new_level.dat',
                title='Save level',
                defaultextension='dat',
                filetypes=[("Level files", "*.dat")]
            )

            if not path:
                return

            self.opened_level_path = os.path.relpath(path, start=os.getcwd())

        with open(self.opened_level_path, 'wb') as f:
            pickle.dump(data, f)
        print(f"Saved to {self.opened_level_path}.")

    def open(self):
        path = tkinter.filedialog.askopenfilename(
            initialdir=self.levels_path,
            title='Open level',
            filetypes=[("Level files", "*.dat")]
        )

        if not path:
            return

        self.opened_level_path = os.path.relpath(path, start=os.getcwd())
        with open(self.opened_level_path, 'rb') as f:
            level = pickle.load(f)
            self.load_level(level)

        print(f"Opened from {self.opened_level_path}")

    def _process_events(self, evt):
        match evt.type:
            case pg.WINDOWCLOSE:
                self.close()
            case pgui.UI_BUTTON_PRESSED:
                if evt.ui_element == self.menu.save_btn:
                    self.save()
                elif evt.ui_element == self.menu.open_btn:
                    self.open()
                elif evt.ui_element == self.menu.new_btn:
                    self.new_level()

        self.board.process_events(evt)

    def _update(self, dt):
        self.board.update()
        self.sprites.update()

    def _draw(self, surface) -> list[Rect | RectType]:
        return self.sprites.draw(surface)
