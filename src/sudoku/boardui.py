from pygame.rect import Rect
from pygame import Surface, SRCALPHA
from pygame.sprite import LayeredDirty, DirtySprite
from pygame_gui.core import IContainerLikeInterface
from pygame_gui.core.interfaces import IUIManagerInterface

from .board import Board
from .rules.rule import RuleManager
from .rules.killer import KillerRule
from .rules.surround import SurroundRule
from .rules.dots import DotRule


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

        self.rule_layer_under = DirtySprite()
        self.rule_layer_under.image = Surface(self.grid.image.get_size(), SRCALPHA)
        self.rule_layer_under.rect = Rect(self.grid.rect)

        self.rule_layer_above = DirtySprite()
        self.rule_layer_above.image = Surface(self.grid.image.get_size(), SRCALPHA)
        self.rule_layer_above.rect = Rect(self.grid.rect)

        sprite_groups.add(self.rule_layer_under, layer=1)
        sprite_groups.add(self.rule_layer_above, layer=4)

        # Event handlers
        self.grid.on_changed.add_handler(self.rule_manager.update)

    def redraw_rules(self):
        self.rule_layer_under.image.fill((0, 0, 0, 0))
        self.rule_layer_above.image.fill((0, 0, 0, 0))
        for _ in self.rule_manager.component_rules:
            if isinstance(_, (DotRule, SurroundRule, KillerRule)):
                _.draw(self.rule_layer_above.image, self.tile_size)
            else:
                _.draw(self.rule_layer_under.image, self.tile_size)
        self.rule_layer_above.dirty = 1
        self.rule_layer_under.dirty = 1
