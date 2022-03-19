import pygame as pg

from .app import Application


class Game(Application):

    def __init__(self):
        super().__init__()

    def _process_events(self):
        for evt in pg.event.get():
            match evt.type:
                case pg.WINDOWCLOSE:
                    self.close()
                case pg.KEYDOWN:
                    match evt.key:
                        case pg.K_ESCAPE:
                            self.close()

    def _update(self, dt):
        pass

    def _draw(self):
        pass
