from pygame_gui.ui_manager import UIManager
from pygame_gui.core import layered_gui_group
from pygame.surface import Surface
from pygame.rect import Rect, RectType


class LayeredGUIGroup(layered_gui_group.LayeredGUIGroup):

    def __init__(self):
        super().__init__()

    def draw(self, surface) -> list[Rect | RectType]:
        return surface.blits(self.visible)


class GUIManager(UIManager):

    def __init__(self, window_size: tuple[int, int]):
        super().__init__(window_size)
        self.ui_group = LayeredGUIGroup()

    def draw_ui(self, window_surface: Surface) -> list[Rect | RectType]:
        return self.ui_group.draw(window_surface)
