import os

from core.app import Application
from sudoku.board import InputMode
from sudoku.level import Level
from .ui.rule_list import RuleListPanel
from .ui.properties import PropertiesPanel
from .ui.menu import Menu
from sudoku.boardui import BoardUI

import pygame as pg
import pygame_gui as pgui
from pygame.sprite import LayeredDirty
from pygame.rect import Rect, RectType
from pygame_gui.elements import UIPanel, UITextEntryLine

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

        self.rule_panel = UIPanel(Rect(10, 10, 300, 800), 0, self.ui_manager)
        self.rule_list = RuleListPanel(Rect(0, 0, 200, 300), self.ui_manager, self.rule_panel)
        self.properties_panel = PropertiesPanel(Rect(0, 300, 200, 300), self.ui_manager, self.rule_panel)
        self.name = UITextEntryLine(Rect(0, 600, 300, 30), self.ui_manager, self.rule_panel)

        self.menu = Menu((400, 650), self.ui_manager)

        self.board = BoardUI(
            (400, 50), 500, 48,
            self.sprites, self.ui_manager
        )

        # Event handlers
        self.rule_list.on_rule_selected.add_handler(self.properties_panel.set_rule)
        self.properties_panel.on_applied.add_handler(self.board.redraw_rules)

        self.new_level()

    def load_level(self, level: Level):
        self.name.set_text(level.name)

        self.properties_panel.set_rule(None)
        self.rule_list.set_rule_list(level.ruleset)

        self.board.grid.clear()
        for pos, val in level.start_values.items():
            self.board.grid.fill_tiles(val, InputMode.INPUT_MODE_VALUE, {pos})

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

        self.board.grid.process_events(evt)

    def _update(self, dt):
        self.sprites.update()

    def _draw(self, surface) -> list[Rect | RectType]:
        return self.sprites.draw(surface)
