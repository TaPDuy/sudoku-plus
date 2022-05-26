import os

from core.app import Application
from sudoku.grid import InputMode
from sudoku.level import Level, LevelList
from .ui.rule_list import RuleListPanel
from .ui.properties import PropertiesPanel
from sudoku.board import Board
from core.ui import ButtonGrid

import pygame as pg
import pygame_gui as pgui
from pygame.sprite import LayeredDirty
from pygame.rect import Rect, RectType
from pygame_gui.elements import UIPanel, UITextEntryLine, UILabel

import pickle
import tkinter.filedialog


class LevelMaker(Application):

    def __init__(self):
        super().__init__("Sudoku Level Maker", (1280, 720))

        self.opened_level_path = ""
        self.levels_path = f"{os.getcwd()}/{LevelList.LEVELS_PATH}"
        if not os.path.exists(self.levels_path):
            os.makedirs(self.levels_path)

        self.sprites = LayeredDirty()

        self.left_panel = None
        self.menu = None
        self.rule_list = None

        self.label_1 = None
        self.label_2 = None

        self.right_panel = None
        self.name = None
        self.properties_panel = None

        self.board = None
        self.init_components()
        self.assign_event_handlers()

        self.new_level()

    def init_components(self):
        ratio = self.width / self.height
        board_size = self.height if ratio > 2 else 1/2 * self.width
        self.board = Board(
            (self.width / 2 - board_size / 2, self.height / 2 - board_size / 2),
            board_size, board_size / 11, self.sprites, self.ui_manager
        )
        self.board.hide_timer()

        self.left_panel = UIPanel(
            Rect(0, 0, self.board.rect.left, self.height), 0, self.ui_manager,
            margins={'left': 0, 'right': 0, 'top': 0, 'bottom': 0}
        )

        # self.menu = Menu(Rect(0, 0, self.left_panel.relative_rect.w, 30), self.ui_manager, self.left_panel)
        self.menu = ButtonGrid(
            (3, 1), Rect(0, 0, self.left_panel.relative_rect.w, 30), 5,
            self.ui_manager, self.left_panel
        )
        self.menu.add_button("Save", "save")
        self.menu.add_button("Open", "open")
        self.menu.add_button("New", "new")

        self.rule_list = RuleListPanel(Rect(
            self.menu.relative_rect.bottomleft,
            (self.left_panel.relative_rect.w, self.left_panel.relative_rect.h - self.menu.relative_rect.h)
        ), self.ui_manager, self.left_panel)

        self.right_panel = UIPanel(
            Rect(self.board.rect.right, 0, self.width - self.board.rect.right, self.height), 0, self.ui_manager,
            margins={'left': 0, 'right': 0, 'top': 0, 'bottom': 0}
        )

        pad = 10
        self.label_1 = UILabel(
            Rect(0, pad, self.right_panel.relative_rect.w, 20),
            "Level name", self.ui_manager, self.right_panel
        )
        self.name = UITextEntryLine(Rect(
            pad, self.label_1.relative_rect.bottom + pad,
            self.right_panel.relative_rect.w - 2 * pad, 30
        ), self.ui_manager, self.right_panel)

        self.label_2 = UILabel(
            Rect(
                0, self.name.relative_rect.bottom + pad,
                self.right_panel.relative_rect.w, 20
            ),
            "Rule properties", self.ui_manager, self.right_panel
        )
        self.properties_panel = PropertiesPanel(Rect(
            0, self.label_2.relative_rect.bottom,
            self.left_panel.relative_rect.w,
            self.left_panel.relative_rect.h - self.label_2.relative_rect.bottom
        ), self.ui_manager, self.right_panel)

    def recalculate_componenets(self, new_width, new_height):
        ratio = new_width / new_height
        board_size = new_height if ratio > 2 else 1/2 * new_width
        self.board.resize(
            (new_width / 2 - board_size / 2, new_height / 2 - board_size / 2),
            board_size, board_size / 11
        )

        self.left_panel.set_position((0, 0))
        self.left_panel.set_dimensions((self.board.rect.left, new_height))

        self.menu.set_relative_rect(Rect(0, 0, self.left_panel.relative_rect.w, 30))
        self.rule_list.set_relative_rect(Rect(
            self.menu.relative_rect.bottomleft,
            (self.left_panel.relative_rect.w, self.left_panel.relative_rect.h - self.menu.relative_rect.h)
        ))

        self.right_panel.set_position((self.board.rect.right, 0))
        self.right_panel.set_dimensions((new_width - self.board.rect.right, new_height))

        pad = 10
        self.label_1.set_relative_position((0, pad))
        self.label_1.set_dimensions((self.right_panel.relative_rect.w, 20))

        self.name.set_relative_position((pad, self.label_1.relative_rect.bottom + pad))
        self.name.set_dimensions((self.right_panel.relative_rect.w - 2 * pad, 30))

        self.label_2.set_relative_position((0, self.name.relative_rect.bottom + pad))
        self.label_2.set_dimensions((self.right_panel.relative_rect.w, 20))

        self.properties_panel.set_relative_rect(Rect(
            0, self.label_2.relative_rect.bottom,
            self.right_panel.relative_rect.w, new_height - self.label_2.relative_rect.bottom
        ))

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
            self.board.fill_tiles(val, [pos], InputMode.INPUT_MODE_VALUE, no_record=True)

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
                if evt.ui_element == self.menu.get_button("save"):
                    self.save()
                elif evt.ui_element == self.menu.get_button("open"):
                    self.open()
                elif evt.ui_element == self.menu.get_button("new"):
                    self.new_level()

        self.board.process_events(evt)

    def _update(self, dt):
        self.board.update()
        self.sprites.update()

    def _draw(self, surface) -> list[Rect | RectType]:
        return self.sprites.draw(surface)
