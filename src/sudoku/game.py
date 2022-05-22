import pygame as pg
from pygame.rect import Rect, RectType
from pygame.sprite import LayeredDirty
from pygame_gui.elements import UITextBox
from pygame_gui.core import UIContainer

import core.ui
from core.app import Application
from core.action import ActionManager
from core.ui import ButtonGrid, TabController
from sudoku.grid import InputMode
from sudoku.board import Board
from sudoku.level import Level, LevelList, random_sudoku, generate_level_id
from sudoku.score import Highscore
from sudoku.settings import SettingsPanel

DIM_MATS = \
    (
        (
            (0, 0, 0, 0),
            (-2 / 3, .5, -1 / 3, 1),
            (1, 0, 1, 0),
            (1, 0, 1 / 3, 0)
        ),
        (
            (0, 0, 2 / 3, 0),
            (-1 / 3, .5, 0, 0),
            (2 / 3, 0, 1 / 3, 0),
            (2 / 3, 0, 0, 1)
        ),
        (
            (.5, -2 / 3, 1, -1 / 3),
            (0, 0, 0, 0),
            (0, 1, 0, 1 / 3),
            (0, 1, 0, 1)
        )
    )

CONTROLS_TEXT = (
    "<b>Controls:</b><br>"
    "- 1-9 (or numpad): Fill selections <br>"
    "- Backspace: Delete <br>"
    "- Ctrl-Z, Crtl-Y: Undo/Redo <br>"
    "- Hold Shift: Switch to mode after current mode <br>"
    "- Hold Ctrl: Switch to mode before current mode <br>"
    "- Enter: Pause <br>"
    "- Escape: Exit <br>"
)


class Game(Application):

    def __init__(self):
        super().__init__((1080, 720))

        core.ui.init()

        self.sprites = LayeredDirty()
        self.tabs = TabController()
        self.paused = False
        self.win = False

        self.main_panel = None
        self.game_panel = None
        self.side_panel = None
        self.board = None
        self.input = None

        self.menu = None
        self.rule_desc = None
        self.controls = None
        self.level_list = None
        self.settings = None

        self.init_components()
        self.init_events()

        self.loaded_id = None
        self.loaded_level = random_sudoku()
        self.load_level(self.loaded_level)

    def init_components(self):
        ratio = self.width / self.height
        index = 0 if ratio <= 3 / 4 else (1 if ratio < 4 / 3 else 2)

        main_rect = Rect(*(DIM_MATS[index][_][0] * self.width + DIM_MATS[index][_][1] * self.height for _ in range(4)))
        side_rect = Rect(*(DIM_MATS[index][_][2] * self.width + DIM_MATS[index][_][3] * self.height for _ in range(4)))

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

        self.board = Board(
            main_rect.topleft, main_rect.height, main_rect.height / 11,
            self.sprites, self.ui_manager, title_height=main_rect.height / 22
        )

        self.side_panel = UIContainer(Rect(side_rect.topleft, side_rect.size), self.ui_manager)

        self.input = ButtonGrid((4, 4), input_rect, 5, self.ui_manager, self.side_panel)
        self.input.add_button("7", "7", keys=[pg.K_7, pg.K_KP7])
        self.input.add_button("8", "8", keys=[pg.K_8, pg.K_KP8])
        self.input.add_button("9", "9", keys=[pg.K_9, pg.K_KP9])
        self.input.add_button("Value", "value", sticky=True)
        self.input.add_button("4", "4", keys=[pg.K_4, pg.K_KP4])
        self.input.add_button("5", "5", keys=[pg.K_5, pg.K_KP5])
        self.input.add_button("6", "6", keys=[pg.K_6, pg.K_KP6])
        self.input.add_button("Mark", "mark", sticky=True)
        self.input.add_button("1", "1", keys=[pg.K_1, pg.K_KP1])
        self.input.add_button("2", "2", keys=[pg.K_2, pg.K_KP2])
        self.input.add_button("3", "3", keys=[pg.K_3, pg.K_KP3])
        self.input.add_button("Color", "color", sticky=True)
        self.input.add_button("Undo", "undo")
        self.input.add_button("Redo", "redo")
        self.input.add_button("Check", "check")
        self.input.add_button("Reset", "reset")
        self.board.set_focusable_areas(self.board.grid_rect, self.input.rect)

        self.menu = ButtonGrid((4, 1) if vertical else (1, 4), menu_rect, 5, self.ui_manager, self.side_panel)
        self.menu.add_button("Rules", "rules", sticky=True)
        self.menu.add_button("Controls", "controls", sticky=True)
        self.menu.add_button("Settings", "settings", sticky=True)
        self.menu.add_button("Levels", "levels", sticky=True)

        self.rule_desc = UITextBox("", desc_rect, self.ui_manager, container=self.side_panel)
        self.controls = UITextBox(CONTROLS_TEXT, desc_rect, self.ui_manager, container=self.side_panel)

        self.level_list = LevelList(desc_rect, self.ui_manager, self.side_panel)
        self.level_list.load_levels()

        self.settings = SettingsPanel(desc_rect, self.ui_manager, self.side_panel)
        self.settings.add_setting("Fullscreen", "fullscreen")
        self.settings.add_setting("Toggle highlight", "highlight", True)

        self.tabs.add_tab(self.rule_desc)
        self.tabs.add_tab(self.controls)
        self.tabs.add_tab(self.settings)
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
        self.settings.set_relative_rect(desc_rect)

    def init_events(self):
        self.level_list.on_load_requested.add_handler(self.load_level)

        self.menu.on_button_pressed.add_handler(self.handle_menu_buttons)
        self.input.on_button_pressed.add_handler(self.handle_input_buttons)

        self.settings.on_changed.add_handler(self.handle_settings_changes)
        self.tabs.on_tab_switched.add_handler(self.settings.discard_changes)

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
        self.board.unlock()
        self.board.grid.clear()
        for pos, val in level.start_values.items():
            self.board.fill_tiles(val, [pos], InputMode.INPUT_MODE_VALUE, lock=True, no_record=True)

        self.win = False
        self.board.playing = False
        self.board.timer.stop()
        self.board.timer.reset()

        # Draw component rules
        self.board.set_title(level.name)
        self.board.set_highscore(Highscore.get(level_id))
        self.board.redraw_rules()

        if self.paused:
            self.board.title.set_text(self.board.title_text.upper() + " (PAUSED)")
            self.board.lock()

    def check_win(self):
        if self.board.check_win_conditions():
            self.win = True
            self.board.lock()
            new_best = Highscore.update(self.loaded_id, self.board.timer.time)
            self.board.title.set_text(
                self.board.title_text.upper() +
                (" (NEW RECORD)" if new_best else " (COMPLETED)")
            )

    def pause(self):
        if self.paused and not self.win:
            self.paused = False
            self.board.set_title(self.board.title_text.upper())
            self.board.unlock()
        else:
            self.paused = True
            self.board.title.set_text(self.board.title_text.upper() + " (PAUSED)")
            self.board.lock()

    def _process_events(self, evt):
        match evt.type:
            case pg.WINDOWCLOSE:
                self.close()
            case pg.KEYDOWN:
                match evt.key:
                    case pg.K_ESCAPE:
                        self.close()
                    case pg.K_RETURN:
                        self.pause()
                    case pg.K_z:
                        if not self.paused and evt.mod & pg.KMOD_CTRL:
                            ActionManager.undo()
                    case pg.K_y:
                        if not self.paused and evt.mod & pg.KMOD_CTRL:
                            ActionManager.redo()

        self.board.process_events(evt)

    def handle_settings_changes(self, changes: dict):
        if "fullscreen" in changes:
            self.set_fullscreen(changes["fullscreen"])
        if "highlight" in changes:
            self.board.set_enable_highlight(changes["highlight"])

    def handle_menu_buttons(self, button_id: str):
        match button_id:
            case "rules":
                self.tabs.set_tab(0)
            case "controls":
                self.tabs.set_tab(1)
            case "settings":
                self.tabs.set_tab(2)
            case "levels":
                self.tabs.set_tab(3)

    def handle_input_buttons(self, button_id: str):
        match button_id:
            case "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9":
                self.board.fill_selection(int(button_id))
            case "value":
                self.board.force_mode = InputMode.INPUT_MODE_VALUE
            case "mark":
                self.board.force_mode = InputMode.INPUT_MODE_MARK
            case "color":
                self.board.force_mode = InputMode.INPUT_MODE_COLOR
            case "undo":
                if not self.paused:
                    ActionManager.undo()
            case "redo":
                if not self.paused:
                    ActionManager.redo()
            case "check":
                if not self.win:
                    self.check_win()
            case "reset":
                self.reset()

    def _update(self, dt):
        self.board.update()
        self.sprites.update()

    def _draw(self, surface) -> list[Rect | RectType]:
        return self.sprites.draw(surface)
