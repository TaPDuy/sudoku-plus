from pygame.rect import Rect
from pygame import Surface, SRCALPHA
from pygame.sprite import LayeredDirty, DirtySprite
from pygame_gui.core import IContainerLikeInterface
from pygame_gui.core.interfaces import IUIManagerInterface

from .board import Board
from .rules.rule import RuleManager
from .rules.killer import KillerRule


class BoardUI:

    def __init__(self, pxpos: tuple[float, float], pxsize: float, padding: float, sprite_groups: LayeredDirty, manager: IUIManagerInterface, container: IContainerLikeInterface = None):
        self.pxpos = self.pxx, self.pxy = pxpos
        if container:
            container_rect = container.get_container().get_rect()
            self.pxpos = self.pxx, self.pxy = container_rect.x + self.pxx, container_rect.y + self.pxy

        self.pxsize = self.pxw, self.pxh = pxsize, pxsize
        self.padding = padding

        px_grid_size = self.pxw - padding * 2, self.pxh - padding * 2
        self.tile_size = self.tlw, self.tlh = px_grid_size[0] / 9, px_grid_size[1] / 9

        # Components
        self.grid = Board((self.pxx + padding, self.pxy + padding), px_grid_size, sprite_groups, manager)

        self.rule_manager = RuleManager(self.grid)

        KillerRule.generate_killer_mesh(self.tile_size)

        under = DirtySprite()
        under.image = Surface(self.grid.image.get_size(), SRCALPHA)
        under.rect = Rect(self.grid.rect)

        above = DirtySprite()
        above.image = Surface(self.grid.image.get_size(), SRCALPHA)
        above.rect = Rect(self.grid.rect)

        sprite_groups.add(under, layer=1)
        sprite_groups.add(above, layer=4)

        # Event handlers
        self.grid.on_changed.add_handler(self.rule_manager.update)
