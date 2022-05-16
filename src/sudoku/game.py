import pygame as pg
import pygame_gui as pgui
from pygame.rect import Rect, RectType
from pygame.sprite import LayeredDirty
from pygame_gui.elements import UITextBox
from pygame_gui.core import UIContainer

from core.app import Application
from core.action import ActionManager
from core.ui import ButtonGrid, TabController
from sudoku.grid import InputMode
from sudoku.board import Board
from sudoku.input import InputPanel
from sudoku.level import Level, LevelList, random_sudoku, generate_level_id
from sudoku.score import Highscore
from core.audio import BgmPlayer

from functools import partial


DIM_MATS = \
    (
        (
            (0, 0, 0, 0),
            (-2/3, .5, -1/3, 1),
            (1, 0, 1, 0),
            (1, 0, 1/3, 0)
        ),
        (
            (0, 0, 2/3, 0),
            (-1/3, .5, 0, 0),
            (2/3, 0, 1/3, 0),
            (2/3, 0, 0, 1)
        ),
        (
            (.5, -2/3, 1, -1/3),
            (0, 0, 0, 0),
            (0, 1, 0, 1/3),
            (0, 1, 0, 1)
        )
    )


class Game(Application):

    def __init__(self):
        super().__init__((1080, 720))
        self.sprites = LayeredDirty()
        self.tabs = TabController()

        self.main_panel = None
        self.game_panel = None
        self.side_panel = None
        self.board = None
        self.input = None

        self.menu = None
        self.rule_desc = None
        self.controls = None
        self.level_list = None
        self.player = None

        self.init_components()
        self.init_events()

        self.loaded_id = None
        self.loaded_level = random_sudoku()
        self.load_level(self.loaded_level)

    def init_components(self):
        ratio = self.width / self.height
        index = 0 if ratio <= 3/4 else (1 if ratio < 4/3 else 2)

        main_rect = Rect(*(DIM_MATS[index][_][0] * self.width + DIM_MATS[index][_][1] * self.height for _ in range(4)))
        side_rect = Rect(*(DIM_MATS[index][_][2] * self.width + DIM_MATS[index][_][3] * self.height for _ in range(4)))

        vertical = ratio > 3/4
        input_rect = Rect(0, 0, side_rect.w, side_rect.w) if vertical else Rect(0, 0, side_rect.h, side_rect.h)
        menu_rect = Rect(
            input_rect.bottomleft, (side_rect.w, side_rect.w / 4)
        ) if vertical else Rect(
            input_rect.topright, (side_rect.h / 4, side_rect.h)
        )
        desc_rect = Rect(
            menu_rect.bottomleft, (side_rect.w, side_rect.h - input_rect.h - menu_rect.h)
        ) if vertical else Rect(
            menu_rect.topright, (side_rect.w - input_rect.w - menu_rect.w, side_rect.h)
        )

        self.board = Board(
            main_rect.topleft, main_rect.height, main_rect.height / 11,
            self.sprites, self.ui_manager, self.main_panel, main_rect.height / 22
        )

        self.side_panel = UIContainer(Rect(side_rect.topleft, side_rect.size), self.ui_manager)

        self.input = InputPanel(input_rect, (8, 8), self.ui_manager, container=self.side_panel)
        for _ in range(9):
            self.input.assign(_, partial(self.board.fill_selection, _ + 1))
        self.input.assign(InputPanel.BUTTON_VALUE, partial(self.select_input_mode, InputPanel.BUTTON_VALUE))
        self.input.assign(InputPanel.BUTTON_MARK, partial(self.select_input_mode, InputPanel.BUTTON_MARK))
        self.input.assign(InputPanel.BUTTON_COLOR, partial(self.select_input_mode, InputPanel.BUTTON_COLOR))
        self.input.assign(InputPanel.BUTTON_UNDO, ActionManager.undo)
        self.input.assign(InputPanel.BUTTON_REDO, ActionManager.redo)
        self.input.assign(InputPanel.BUTTON_CHECK, self.check_win)
        self.input.assign(InputPanel.BUTTON_RESET, self.reset)
        self.board.set_focusable_areas(self.board.grid_rect, self.input.rect)

        self.menu = ButtonGrid((4, 1) if vertical else (1, 4), menu_rect, 5, self.ui_manager, self.side_panel)
        self.menu.add_button("Rules", "rules")
        self.menu.add_button("Controls", "controls")
        self.menu.add_button("Settings", "settings")
        self.menu.add_button("Levels", "levels")

        self.rule_desc = UITextBox("", desc_rect, self.ui_manager, container=self.side_panel)
        self.controls = UITextBox("--- Controls ---", desc_rect, self.ui_manager, container=self.side_panel)

        self.level_list = LevelList(desc_rect, self.ui_manager, self.side_panel)
        self.level_list.load_levels()

        self.player = BgmPlayer(desc_rect, self.ui_manager, self.side_panel)
        self.player.load_bgm()
        self.player.play()

        self.tabs.add_tab(self.rule_desc)
        self.tabs.add_tab(self.controls)
        self.tabs.add_tab(self.player)
        self.tabs.add_tab(self.level_list)

    def recalculate_componenets(self, new_width, new_height):
        ratio = new_width / new_height
        index = 0 if ratio <= 3 / 4 else (1 if ratio < 4 / 3 else 2)

        main_rect = Rect(*(DIM_MATS[index][_][0] * new_width + DIM_MATS[index][_][1] * new_height for _ in range(4)))
        side_rect = Rect(*(DIM_MATS[index][_][2] * new_width + DIM_MATS[index][_][3] * new_height for _ in range(4)))

        vertical = ratio > 3 / 4
        input_rect = Rect(0, 0, side_rect.w, side_rect.w) if vertical else Rect(0, 0, side_rect.h, side_rect.h)
        menu_rect = Rect(
            input_rect.bottomleft, (side_rect.w, side_rect.w / 4)
        ) if vertical else Rect(
            input_rect.topright, (side_rect.h / 4, side_rect.h)
        )
        desc_rect = Rect(
            menu_rect.bottomleft, (side_rect.w, side_rect.h - input_rect.h - menu_rect.h)
        ) if vertical else Rect(
            menu_rect.topright, (side_rect.w - input_rect.w - menu_rect.w, side_rect.h)
        )

        self.board.resize(main_rect.topleft, main_rect.height, main_rect.height / 11, main_rect.height / 22)

        self.side_panel.set_position(side_rect.topleft)
        self.side_panel.set_dimensions(side_rect.size)

        self.input.set_relative_rect(input_rect)
        self.board.set_focusable_areas(self.board.grid_rect, self.input.rect)

        self.menu.set_relative_rect(menu_rect)
        self.menu.set_grid_size((4, 1) if vertical else (1, 4))

        self.rule_desc.set_relative_position(desc_rect.topleft)
        self.rule_desc.set_dimensions(desc_rect.size)
        self.controls.set_relative_position(desc_rect.topleft)
        self.controls.set_dimensions(desc_rect.size)
        self.level_list.set_relative_rect(desc_rect)
        self.player.set_relative_rect(desc_rect)

    def init_events(self):
        self.level_list.on_load_requested.add_handler(self.load_level)

    def reset(self):
        self.load_level(self.loaded_level, self.loaded_id)

    def load_level(self, level: Level, level_id: str = None):
        self.loaded_id = level_id or generate_level_id()
        self.loaded_level = level

        # Load rules
        self.board.rule_manager.clear_rule()
        self.board.rule_manager.add_rule(level.ruleset)

        types = {type(rule) for rule in level.ruleset}
        self.rule_desc.set_text("--- Ruleset ---<br>" + "<br>".join(" - " + _.DESCRIPTIONS for _ in types))

        # Load initial values
        self.board.grid.clear()
        for pos, val in level.start_values.items():
            self.board.fill_tiles(val, [pos], InputMode.INPUT_MODE_VALUE, lock=True, no_record=True)

        self.board.timer.stop()
        self.board.timer.reset()

        # Draw component rules
        self.board.set_title(level.name)
        self.board.set_highscore(Highscore.get(level_id))
        self.board.redraw_rules()

    def check_win(self):
        if self.board.rule_manager.check():
            Highscore.update(self.loaded_id, self.board.timer.stop())
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
            case pgui.UI_BUTTON_PRESSED:
                if evt.ui_element == self.menu.get_button("rules"):
                    self.tabs.set_tab(0)
                elif evt.ui_element == self.menu.get_button("controls"):
                    self.tabs.set_tab(1)
                elif evt.ui_element == self.menu.get_button("settings"):
                    self.tabs.set_tab(2)
                elif evt.ui_element == self.menu.get_button("levels"):
                    self.tabs.set_tab(3)

        self.input.process_events(evt)
        self.board.process_events(evt)

    def _update(self, dt):
        self.board.update()
        self.sprites.update()

    def _draw(self, surface) -> list[Rect | RectType]:
        return self.sprites.draw(surface)
