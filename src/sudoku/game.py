import pygame as pg
from pygame.rect import Rect, RectType
from pygame.sprite import LayeredDirty, DirtySprite
from pygame_gui.elements import UITextBox

from core.app import Application
from core.action import ActionManager
from sudoku.board import Board, InputMode
from sudoku.input import InputPanel
from sudoku.level import Level, LevelList, random_sudoku
from sudoku.rules.rule import RuleManager
from sudoku.rules.killer import KillerRule
from sudoku.rules.dots import DotRule
from sudoku.rules.surround import SurroundRule
from core.audio import BgmPlayer

from functools import partial


class Game(Application):

    def __init__(self):
        super().__init__((1080, 720))
        self.sprites = LayeredDirty()

        self.board = Board((32, 32), self.sprites, self.ui_manager)

        # Rules
        self.rule_manager = RuleManager(self.board)

        under = DirtySprite()
        under.image = pg.Surface(self.board.image.get_size(), pg.SRCALPHA)
        under.rect = Rect(self.board.rect)

        above = DirtySprite()
        above.image = pg.Surface(self.board.image.get_size(), pg.SRCALPHA)
        above.rect = Rect(self.board.rect)

        self.sprites.add(under, layer=1)
        self.sprites.add(above, layer=4)

        self.input = InputPanel((500, 48), self.ui_manager)
        for _ in range(9):
            self.input.assign(_, partial(self.board.fill_selection, _ + 1))
        self.input.assign(InputPanel.BUTTON_VALUE, partial(self.select_input_mode, InputPanel.BUTTON_VALUE))
        self.input.assign(InputPanel.BUTTON_MARK, partial(self.select_input_mode, InputPanel.BUTTON_MARK))
        self.input.assign(InputPanel.BUTTON_COLOR, partial(self.select_input_mode, InputPanel.BUTTON_COLOR))
        self.input.assign(InputPanel.BUTTON_UNDO, ActionManager.undo)
        self.input.assign(InputPanel.BUTTON_REDO, ActionManager.redo)
        self.input.assign(InputPanel.BUTTON_CHECK, self.check_win)
        self.board.set_focusable_areas(self.board.rect, self.input.rect)

        self.level_list = LevelList(Rect(500, 250, 175, 200), self.ui_manager)
        self.level_list.load_levels()

        self.player = BgmPlayer(Rect(500, 500, 200, 150), self.ui_manager)
        self.player.load_bgm()
        self.player.play()

        self.rule_desc = UITextBox("", Rect(50, 500, 400, 200), self.ui_manager)

        # Event handlers
        self.level_list.on_load_requested.add_handler(self.load_level)
        self.board.on_changed.add_handler(self.rule_manager.update)

        KillerRule.generate_killer_mesh()

        self.load_level(random_sudoku())

    def load_level(self, level: Level):
        # Load rules
        self.rule_manager.clear_rule()
        self.rule_manager.add_rule(level.ruleset)

        types = {type(rule) for rule in level.ruleset}
        self.rule_desc.set_text("--- Ruleset ---<br>" + "<br>".join(" - " + _.DESCRIPTIONS for _ in types))

        # Load initial values
        self.board.clear()
        for pos, val in level.start_values.items():
            self.board.fill_tiles(val, InputMode.INPUT_MODE_VALUE, [pos])
        self.board.lock_tile(list(level.start_values.keys()), True)

        # Draw component rules
        above = self.sprites.get_sprites_from_layer(4)
        under = self.sprites.get_sprites_from_layer(1)
        above[0].image.fill((0, 0, 0, 0))
        under[0].image.fill((0, 0, 0, 0))
        for _ in self.rule_manager.component_rules:
            if isinstance(_, (DotRule, SurroundRule, KillerRule)):
                _.draw(above[0].image)
            else:
                _.draw(under[0].image)

    def check_win(self):
        if self.rule_manager.check():
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
        self.sprites.update()

    def _draw(self, surface) -> list[Rect | RectType]:
        return self.sprites.draw(surface)
