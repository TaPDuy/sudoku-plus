from . import Application
from .makerui import PropertiesPanel, RuleListPanel
from .sudoku import Board

import pygame as pg
from pygame.sprite import LayeredDirty
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

        # Event handlers
        self.rule_list.on_rule_selected.add_handler(self.properties_panel.set_rule)

    def _process_events(self, evt):
        match evt.type:
            case pg.WINDOWCLOSE:
                self.close()

        self.board.process_events(evt)

    def _update(self, dt):
        self.sprites.update()

    def _draw(self, surface) -> list[Rect | RectType]:
        return self.sprites.draw(surface)
