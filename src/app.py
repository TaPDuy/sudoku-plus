import time
import pygame as pg
from pygame.rect import Rect, RectType


class Application:
    TARGET_FPS = 60
    CLEAR_COLOR = (100, 20, 50)

    def __init__(self, size: tuple[int, int] = (600, 600)):
        pg.init()
        self._clock = pg.time.Clock()
        self._screen = pg.display.set_mode(size)
        self._font = pg.font.SysFont("Consolas", 14)

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

            self._process_events()
            self._update(dt * Application.TARGET_FPS)

            self._screen.fill(Application.CLEAR_COLOR)
            rects = self._draw(self._screen)

            textsurface = self._font.render(f"FPS: {int(self._clock.get_fps())}", False, (255, 255, 255))
            rects.append(self._screen.blit(textsurface, (0, 0)))

            pg.display.update(rects)
            self._clock.tick(0)

    def close(self):
        self.is_running = False

    def _process_events(self):
        pass

    def _update(self, dt):
        pass

    def _draw(self, surface) -> list[Rect | RectType]:
        pass
