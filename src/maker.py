from . import Application
from .makerui import PropertiesPanel, RuleListPanel
from .sudoku import Board
from .sudoku.rules import ComponentRule, DotRule, SurroundRule, KillerRule

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

        under = DirtySprite()
        under.image = pg.Surface(self.board.image.get_size(), pg.SRCALPHA)
        under.rect = Rect(self.board.rect)

        above = DirtySprite()
        above.image = pg.Surface(self.board.image.get_size(), pg.SRCALPHA)
        above.rect = Rect(self.board.rect)

        self.sprites.add(under, layer=1)
        self.sprites.add(above, layer=4)

        # Event handlers
        self.rule_list.on_rule_selected.add_handler(self.properties_panel.set_rule)
        self.rule_list.on_rule_selected.add_handler(self.redraw_board)

    def redraw_board(self):
        above = self.sprites.get_sprites_from_layer(4)
        under = self.sprites.get_sprites_from_layer(1)
        above[0].image.fill((0, 0, 0, 0))
        under[0].image.fill((0, 0, 0, 0))
        for _ in self.rule_list.selected_rules:
            if isinstance(_, ComponentRule):
                if isinstance(_, (DotRule, SurroundRule, KillerRule)):
                    _.draw(above[0].image)
                else:
                    _.draw(under[0].image)

    def _process_events(self, evt):
        match evt.type:
            case pg.WINDOWCLOSE:
                self.close()

        self.board.process_events(evt)

    def _update(self, dt):
        self.sprites.update()

    def _draw(self, surface) -> list[Rect | RectType]:
        return self.sprites.draw(surface)
