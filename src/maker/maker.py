from core.app import Application
from sudoku.board import Board
from sudoku.rules.rule import ComponentRule
from sudoku.rules.killer import KillerRule
from sudoku.rules.dots import DotRule
from sudoku.rules.surround import SurroundRule
from .ui.rule_list import RuleListPanel
from .ui.properties import PropertiesPanel

import pygame as pg
from pygame.sprite import LayeredDirty, DirtySprite
from pygame.rect import Rect, RectType
from pygame_gui.elements import UIPanel


class LevelMaker(Application):

    def __init__(self):
        super().__init__((1080, 720))

        self.rule_panel = UIPanel(Rect(10, 10, 300, 700), 0, self.ui_manager)
        self.rule_list = RuleListPanel(Rect(0, 0, 200, 300), self.ui_manager, self.rule_panel)

        self.properties_panel = PropertiesPanel(Rect(0, 300, 200, 300), self.ui_manager, self.rule_panel)

        self.sprites = LayeredDirty()
        self.board = Board((400, 32), self.sprites)

        # Ruleset
        KillerRule.generate_killer_mesh()

        self.under = DirtySprite()
        self.under.image = pg.Surface(self.board.image.get_size(), pg.SRCALPHA)
        self.under.rect = Rect(self.board.rect)

        self.above = DirtySprite()
        self.above.image = pg.Surface(self.board.image.get_size(), pg.SRCALPHA)
        self.above.rect = Rect(self.board.rect)

        self.sprites.add(self.under, layer=1)
        self.sprites.add(self.above, layer=4)

        # Event handlers
        self.rule_list.on_rule_selected.add_handler(self.properties_panel.set_rule)
        self.properties_panel.on_applied.add_handler(self.redraw_board)

    def redraw_board(self):
        self.above.image.fill((0, 0, 0, 0))
        self.under.image.fill((0, 0, 0, 0))
        for _ in self.rule_list.selected_rules:
            if isinstance(_, ComponentRule):
                if isinstance(_, (DotRule, SurroundRule, KillerRule)):
                    _.draw(self.above.image)
                else:
                    _.draw(self.under.image)
        self.above.dirty = 1
        self.under.dirty = 1

    def _process_events(self, evt):
        match evt.type:
            case pg.WINDOWCLOSE:
                self.close()

        self.board.process_events(evt)

    def _update(self, dt):
        self.sprites.update()

    def _draw(self, surface) -> list[Rect | RectType]:
        return self.sprites.draw(surface)
