import time
import pygame as pg
from pygame.rect import Rect, RectType

from core.gfx.ui import GUIManager

pg.init()
pg.font.init()


class Application:
    TARGET_FPS = 60
    CLEAR_COLOR = (10, 0, 20)

    def __init__(self, size: tuple[int, int] = (700, 500)):
        self._clock = pg.time.Clock()
        self.size = self.width, self.height = size

        self.info = pg.display.Info()
        self._screen = pg.display.set_mode(size, pg.RESIZABLE)
        self._font = pg.font.SysFont("Consolas", 14)

        self.ui_manager = GUIManager(size)

        self.is_running = False

    def run(self):
        self._screen.fill(Application.CLEAR_COLOR)
        pg.display.update()

        self.is_running = True
        last_time = time.time()
        while self.is_running:

            new_time = time.time()
            dt = new_time - last_time
            last_time = new_time

            rects = []

            for evt in pg.event.get():
                if evt.type == pg.VIDEORESIZE:
                    print(f"Resized to {evt.w}x{evt.h}")
                    self.recalculate_componenets(evt.w, evt.h)
                    self.ui_manager.set_window_resolution((evt.w, evt.h))
                    self.size = self.width, self.height = evt.w, evt.h

                    self._screen.fill(Application.CLEAR_COLOR)
                    pg.display.update()

                self._process_events(evt)
                self.ui_manager.process_events(evt)

            self._update(dt * Application.TARGET_FPS)
            self.ui_manager.update(dt * Application.TARGET_FPS)

            self._screen.fill(Application.CLEAR_COLOR)
            rects += self._draw(self._screen)
            ui_rects = self.ui_manager.draw_ui(self._screen)
            if ui_rects:
                rects += ui_rects

            textsurface = self._font.render(f"FPS: {int(self._clock.get_fps())}", False, (255, 255, 255))
            rects.append(self._screen.blit(textsurface, (0, 0)))

            pg.display.update(rects)
            self._clock.tick(0)

    def set_fullscreen(self, b: bool):
        pg.display.quit()
        pg.display.init()

        size = (self.info.current_w, self.info.current_h) if b else self.size
        mode = pg.FULLSCREEN if b else pg.RESIZABLE

        self._screen = pg.display.set_mode(size, mode)
        self.recalculate_componenets(*size)
        self.ui_manager.set_window_resolution(size)

        self._screen.fill(Application.CLEAR_COLOR)
        pg.display.update()

    def close(self):
        self.is_running = False

    def recalculate_componenets(self, new_width, new_height):
        pass

    def _process_events(self, evt):
        pass

    def _update(self, dt):
        pass

    def _draw(self, surface) -> list[Rect | RectType]:
        pass
