import pygame as pg
from pygame.rect import Rect, RectType
from pygame.sprite import LayeredDirty
from pygame_gui.elements import UITextBox
from pygame_gui.core import UIContainer

from core.app import Application
from core.action import ActionManager
from sudoku.board import InputMode
from sudoku.boardui import BoardUI
from sudoku.input import InputPanel
from sudoku.level import Level, LevelList, random_sudoku
from sudoku.rules.killer import KillerRule
from sudoku.rules.dots import DotRule
from sudoku.rules.surround import SurroundRule
from core.audio import BgmPlayer

from functools import partial


class Game(Application):

    def __init__(self):
        super().__init__((1080, 720))
        self.sprites = LayeredDirty()

        self.level_list = LevelList(Rect(900, 250, 175, 200), self.ui_manager)
        self.level_list.load_levels()

        self.player = BgmPlayer(Rect(900, 500, 200, 150), self.ui_manager)
        self.player.load_bgm()
        self.player.play()

        self.main_panel = None
        self.game_panel = None
        self.side_panel = None
        self.board = None
        self.input = None
        self.rule_desc = None
        self.init_components()

        # Event handlers
        self.level_list.on_load_requested.add_handler(self.load_level)

        self.load_level(random_sudoku())

    def init_components(self):
        main_panel_size = min(self.size)
        self.main_panel = UIContainer(Rect(
            self.width / 2 - main_panel_size / 2,
            self.height / 2 - main_panel_size / 2,
            main_panel_size, main_panel_size
        ), self.ui_manager)

        self.game_panel = UIContainer(Rect(
            0, 0, main_panel_size * 2 / 3, main_panel_size
        ), self.ui_manager, container=self.main_panel)

        self.board = BoardUI(
            (0, 0), self.game_panel.relative_rect.width, 48,
            self.sprites, self.ui_manager, self.game_panel
        )

        self.side_panel = UIContainer(Rect(
            main_panel_size * 2 / 3, 0, main_panel_size / 3, main_panel_size
        ), self.ui_manager, container=self.main_panel)

        self.input = InputPanel(Rect(
            0, 0, self.side_panel.relative_rect.width, self.side_panel.relative_rect.width
        ), (8, 8), self.ui_manager, container=self.side_panel)
        for _ in range(9):
            self.input.assign(_, partial(self.board.grid.fill_selection, _ + 1))
        self.input.assign(InputPanel.BUTTON_VALUE, partial(self.select_input_mode, InputPanel.BUTTON_VALUE))
        self.input.assign(InputPanel.BUTTON_MARK, partial(self.select_input_mode, InputPanel.BUTTON_MARK))
        self.input.assign(InputPanel.BUTTON_COLOR, partial(self.select_input_mode, InputPanel.BUTTON_COLOR))
        self.input.assign(InputPanel.BUTTON_UNDO, ActionManager.undo)
        self.input.assign(InputPanel.BUTTON_REDO, ActionManager.redo)
        self.input.assign(InputPanel.BUTTON_CHECK, self.check_win)
        self.board.grid.set_focusable_areas(self.board.grid.rect, self.input.rect)

        self.rule_desc = UITextBox("", Rect(
            self.input.relative_rect.bottomleft,
            (self.side_panel.relative_rect.width, self.side_panel.relative_rect.width)
        ), self.ui_manager, container=self.side_panel)

    def load_level(self, level: Level):
        # Load rules
        self.board.rule_manager.clear_rule()
        self.board.rule_manager.add_rule(level.ruleset)

        types = {type(rule) for rule in level.ruleset}
        self.rule_desc.set_text("--- Ruleset ---<br>" + "<br>".join(" - " + _.DESCRIPTIONS for _ in types))

        # Load initial values
        self.board.grid.clear()
        for pos, val in level.start_values.items():
            self.board.grid.fill_tiles(val, InputMode.INPUT_MODE_VALUE, [pos])
        self.board.grid.lock_tile(list(level.start_values.keys()), True)

        # Draw component rules
        above = self.sprites.get_sprites_from_layer(4)
        under = self.sprites.get_sprites_from_layer(1)
        above[0].image.fill((0, 0, 0, 0))
        under[0].image.fill((0, 0, 0, 0))
        for _ in self.board.rule_manager.component_rules:
            if isinstance(_, (DotRule, SurroundRule, KillerRule)):
                _.draw(above[0].image, self.board.tile_size)
            else:
                _.draw(under[0].image, self.board.tile_size)

    def check_win(self):
        if self.board.rule_manager.check():
            print("You win!")
        else:
            print("Something's wrong...")

    def select_input_mode(self, index):
        self.input.toggle_highlight_button(self.board.force_mode.value + InputPanel.BUTTON_VALUE)
        self.input.toggle_highlight_button(index)
        self.board.force_mode = InputMode(index - InputPanel.BUTTON_VALUE)

    def _process_events(self, evt):
        match evt.type:
            case pg.WINDOWCLOSE:
                self.close()
            case pg.KEYDOWN:
                match evt.key:
                    case pg.K_ESCAPE:
                        self.close()
                    case pg.K_z:
                        if evt.mod & pg.KMOD_CTRL:
                            ActionManager.undo()
                    case pg.K_y:
                        if evt.mod & pg.KMOD_CTRL:
                            ActionManager.redo()

        self.input.process_events(evt)
        self.board.grid.process_events(evt)

    def _update(self, dt):
        self.sprites.update()

    def _draw(self, surface) -> list[Rect | RectType]:
        return self.sprites.draw(surface)
