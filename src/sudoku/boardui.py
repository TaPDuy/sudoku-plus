from pygame.rect import Rect
from pygame import Surface, SRCALPHA
from pygame.font import SysFont, Font
from pygame.transform import smoothscale
from pygame.sprite import LayeredDirty, DirtySprite
from pygame_gui.core import IContainerLikeInterface
from pygame_gui.core.interfaces import IUIManagerInterface

from .board import Board
from .rules.rule import RuleManager
from .rules.killer import KillerRule
from .rules.surround import SurroundRule
from .rules.dots import DotRule


class Title:

    def __init__(self, text: str, rect: Rect, sprite_groups: LayeredDirty, align_top=True):
        self.rect = rect
        self.align_top = align_top

        self.__color = (255, 255, 255)
        self.__font = SysFont("Arial", 64)
        self.__base_sprite = self.__font.render(text, True, self.__color)

        self.__text_sprite = DirtySprite(sprite_groups)
        self.__redraw()

    def set_font(self, font: Font):
        self.__font = font
        self.__redraw()

    def set_color(self, color: tuple[int, int, int]):
        self.__color = color
        self.__redraw()

    def set_text(self, text: str):
        self.__base_sprite = self.__font.render(text, True, self.__color)
        self.__redraw()

    def __redraw(self):
        self.__text_sprite.dirty = 1

        height = min(
            self.rect.h,
            self.__base_sprite.get_height() * self.rect.w / self.__base_sprite.get_width()
        )
        self.__text_sprite.rect = Rect(
            (self.rect.left, self.rect.top if self.align_top else self.rect.bottom - height),
            (self.__base_sprite.get_width() * height / self.__base_sprite.get_height(), height)
        )
        self.__text_sprite.image = smoothscale(self.__base_sprite, self.__text_sprite.rect.size)


class BoardUI:

    def __init__(self, pxpos: tuple[float, float], pxsize: float, padding: float, sprite_groups: LayeredDirty, manager: IUIManagerInterface, container: IContainerLikeInterface = None, title_height=20):
        # Properties
        self.rect = self.relative_rect = Rect(pxpos, (pxsize, pxsize))
        if container:
            container_rect = container.get_container().get_rect()
            self.rect = Rect(
                (container_rect.x + self.rect.left, container_rect.y + self.rect.top),
                self.rect.size
            )

        self.padding = padding

        px_grid_size = self.rect.w - padding * 2, self.rect.h - padding * 2
        self.tile_size = self.tlw, self.tlh = px_grid_size[0] / 9, px_grid_size[1] / 9

        # Components
        self.grid = Board(
            (self.rect.left + padding, self.rect.top + padding),
            px_grid_size, sprite_groups, manager
        )
        self.title = Title(" ", Rect(
            (self.grid.pxx, self.grid.pxy - title_height),
            (px_grid_size[0], title_height)
        ), sprite_groups, False)

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

    def set_title(self, title: str):
        if not len(title):
            title = " "
        self.title.set_text(title.upper())

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
