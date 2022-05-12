import pygame as pg
from pygame.rect import Rect, RectType
from pygame.sprite import LayeredDirty
from pygame_gui.elements import UITextBox
from pygame_gui.core import UIContainer

from core.app import Application
from core.action import ActionManager
from sudoku.grid import InputMode
from sudoku.board import Board
from sudoku.input import InputPanel
from sudoku.level import Level, LevelList, random_sudoku
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
        ratio = self.width / self.height
        main_rect = Rect(
            0, .5 * self.height - 3 / 8 * self.width,
            self.width, .75 * self.width
        ) if ratio < 4 / 3 else Rect(
            .5 * self.width - 2 / 3 * self.height, 0,
            4 / 3 * self.height, self.height
        )
        self.main_panel = UIContainer(main_rect, self.ui_manager)

        self.board = Board(
            (0, 0), main_rect.height, main_rect.height / 11,
            self.sprites, self.ui_manager, self.main_panel, main_rect.height / 22
        )

        self.side_panel = UIContainer(Rect(
            self.board.relative_rect.topright, (main_rect.height / 3, main_rect.height)
        ), self.ui_manager, container=self.main_panel)

        self.input = InputPanel(Rect(
            0, 0, self.side_panel.relative_rect.width, self.side_panel.relative_rect.width
        ), (8, 8), self.ui_manager, container=self.side_panel)
        for _ in range(9):
            self.input.assign(_, partial(self.board.fill_selection, _ + 1))
        self.input.assign(InputPanel.BUTTON_VALUE, partial(self.select_input_mode, InputPanel.BUTTON_VALUE))
        self.input.assign(InputPanel.BUTTON_MARK, partial(self.select_input_mode, InputPanel.BUTTON_MARK))
        self.input.assign(InputPanel.BUTTON_COLOR, partial(self.select_input_mode, InputPanel.BUTTON_COLOR))
        self.input.assign(InputPanel.BUTTON_UNDO, ActionManager.undo)
        self.input.assign(InputPanel.BUTTON_REDO, ActionManager.redo)
        self.input.assign(InputPanel.BUTTON_CHECK, self.check_win)
        self.board.set_focusable_areas(self.board.grid_rect, self.input.rect)

        self.rule_desc = UITextBox("", Rect(
            self.input.relative_rect.bottomleft,
            (self.side_panel.relative_rect.width, main_rect.height - self.input.relative_rect.height)
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
            self.board.fill_tiles(val, [pos], InputMode.INPUT_MODE_VALUE, lock=True, no_record=True)

        # Draw component rules
        self.board.set_title(level.name)
        self.board.redraw_rules()

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
        self.board.process_events(evt)

    def _update(self, dt):
        self.board.update()
        self.sprites.update()

    def _draw(self, surface) -> list[Rect | RectType]:
        return self.sprites.draw(surface)
