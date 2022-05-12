import pygame as pg
from pygame.rect import Rect
from pygame import Surface, SRCALPHA
from pygame.font import SysFont, Font
from pygame.transform import smoothscale
from pygame.sprite import LayeredDirty, DirtySprite
from pygame_gui.core import IContainerLikeInterface
from pygame_gui.core.interfaces import IUIManagerInterface

from .board import Board, InputMode
from .selection import SelectionGrid
from .rules.rule import RuleManager
from .rules.killer import KillerRule
from .rules.surround import SurroundRule
from .rules.dots import DotRule
from core.gfx.graphics import Graphics


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
    LAYER_SELECTION = 5
    LAYER_TOP_RULE = 4
    LAYER_NUMBER = 3
    LAYER_GRID = 2
    LAYER_BOTTOM_RULE = 1
    LAYER_COLOR = 0

    TILE_COLORS = (
        (0, 0, 0, 0),
        (100, 100, 100, 255),
        (100, 100, 200, 255),
        (100, 200, 100, 255),
        (100, 200, 200, 255),
        (200, 100, 100, 255),
        (200, 100, 200, 255),
        (200, 200, 100, 255),
        (200, 200, 200, 255),
        (150, 100, 200, 255)
    )

    FONT_VALUE = SysFont("Arial", 48)
    FONT_MARK = SysFont("Arial", 14)

    def __init__(
            self,
            pxpos: tuple[float, float],
            pxsize: float,
            padding: float,
            sprite_groups: LayeredDirty,
            manager: IUIManagerInterface,
            container: IContainerLikeInterface = None,
            title_height=20
    ):
        # Properties
        self.rect = self.relative_rect = Rect(pxpos, (pxsize, pxsize))
        if container:
            container_rect = container.get_container().get_rect()
            self.rect = Rect(
                (container_rect.x + self.rect.left, container_rect.y + self.rect.top),
                self.rect.size
            )

        self.padding = padding

        # Components' properties
        self.grid_rect = Rect(
            self.rect.left + padding, self.rect.top + padding,
            self.rect.w - padding * 2, self.rect.h - padding * 2
        )
        self.grid_relative_rect = Rect((padding, padding), self.grid_rect.size)
        self.tile_size = self.tlw, self.tlh = self.grid_rect.w / 9, self.grid_rect.h / 9

        # Components
        self.grid = Board()
        self.selection = SelectionGrid(Rect(
            self.grid_relative_rect.left - self.tlw / 2,
            self.grid_relative_rect.top - self.tlh / 2,
            self.tlw * 10, self.tlh * 10
        ), self)
        self.rule_manager = RuleManager(self.grid)
        self.title = Title(" ", Rect(
            (self.grid_rect.left, self.grid_rect.top - title_height),
            (self.grid_rect.w, title_height)
        ), sprite_groups, False)
        self.ui_manager = manager

        # Control properties
        self.force_mode = InputMode.INPUT_MODE_VALUE
        self.focusable: list[Rect] = [self.grid_rect]
        self.is_focused = False
        self.multi_select = False
        self.should_select = False

        # Layers
        self.layers = [DirtySprite() for _ in range(6)]

        self.layers[BoardUI.LAYER_COLOR].image = Surface(self.grid_rect.size, SRCALPHA)
        self.layers[BoardUI.LAYER_COLOR].rect = Rect(self.grid_rect)
        sprite_groups.add(self.layers[BoardUI.LAYER_COLOR], layer=BoardUI.LAYER_COLOR)

        self.layers[BoardUI.LAYER_BOTTOM_RULE].image = Surface(self.grid_rect.size, SRCALPHA)
        self.layers[BoardUI.LAYER_BOTTOM_RULE].rect = Rect(self.grid_rect)
        sprite_groups.add(self.layers[BoardUI.LAYER_BOTTOM_RULE], layer=BoardUI.LAYER_BOTTOM_RULE)

        self.layers[BoardUI.LAYER_GRID].image = Surface(self.grid_rect.size, SRCALPHA)
        self.layers[BoardUI.LAYER_GRID].rect = Rect(self.grid_rect)
        sprite_groups.add(self.layers[BoardUI.LAYER_GRID], layer=BoardUI.LAYER_GRID)

        self.layers[BoardUI.LAYER_NUMBER].image = Surface(self.grid_rect.size, SRCALPHA)
        self.layers[BoardUI.LAYER_NUMBER].rect = Rect(self.grid_rect)
        sprite_groups.add(self.layers[BoardUI.LAYER_NUMBER], layer=BoardUI.LAYER_NUMBER)

        self.layers[BoardUI.LAYER_TOP_RULE].image = Surface(self.grid_rect.size, SRCALPHA)
        self.layers[BoardUI.LAYER_TOP_RULE].rect = Rect(self.grid_rect)
        sprite_groups.add(self.layers[BoardUI.LAYER_TOP_RULE], layer=BoardUI.LAYER_TOP_RULE)

        self.layers[BoardUI.LAYER_SELECTION] = self.selection
        sprite_groups.add(self.layers[BoardUI.LAYER_SELECTION], layer=BoardUI.LAYER_SELECTION)

        # Event handlers
        self.grid.on_changed.add_handler(self.rule_manager.update)
        self.grid.on_changed.add_handler(self.draw_tiles)
        self.rule_manager.on_conflict_changed.add_handler(self.grid.highlight_conflicts)

        self.selection.generate_mesh_sprites(.25, (255, 0, 255, 150), 1, (255, 0, 255))
        KillerRule.generate_killer_mesh(self.tile_size)
        self.__initdraw()

    def set_focusable_areas(self, *rects):
        self.focusable = list(rects)

    def process_events(self, evt):
        match evt.type:
            case pg.MOUSEBUTTONDOWN:
                mouse_pos = pg.mouse.get_pos()
                self.is_focused = any(rect.collidepoint(*mouse_pos) for rect in self.focusable)

                if self.is_focused:
                    self.ui_manager.set_focus_set(set())
                else:
                    self.selection.clear()

                if not self.rect.collidepoint(mouse_pos):
                    return
                if not pg.key.get_mods() & pg.KMOD_SHIFT:
                    self.selection.clear()

                self.multi_select = True
                self.should_select = not self.selection.is_selected(self.get_tile_pos(mouse_pos))
            case pg.MOUSEBUTTONUP:
                self.multi_select = False
            case pg.KEYDOWN:
                if not self.is_focused:
                    return
                match evt.key:
                    case pg.K_BACKSPACE:
                        self.fill_selection(0)
                    case pg.K_1 | pg.K_2 | pg.K_3 | pg.K_4 | pg.K_5 | pg.K_6 | pg.K_7 | pg.K_8 | pg.K_9:
                        self.fill_selection(evt.key - pg.K_1 + 1)
                    case pg.K_KP1 | pg.K_KP2 | pg.K_KP3 | pg.K_KP4 | pg.K_KP5 | pg.K_KP6 | pg.K_KP7 | pg.K_KP8 | pg.K_KP9:
                        self.fill_selection(evt.key - pg.K_KP1 + 1)

    def update(self):
        mpos = pg.mouse.get_pos()
        if self.multi_select and self.grid_rect.collidepoint(mpos):
            if self.should_select:
                self.selection.select(self.get_tile_pos((mpos[0] - self.grid_rect.left, mpos[1] - self.grid_rect.top)))
            else:
                self.selection.unselect(self.get_tile_pos((mpos[0] - self.grid_rect.left, mpos[1] - self.grid_rect.top)))

    def fill_selection(self, value):
        self.fill_tiles(value, self.selection.selected)

    def fill_tiles(self, value: int, positions: list | set, mode: InputMode | None = None, **kwargs):
        if not mode:
            mode = InputMode(
                (
                    (pg.key.get_mods() & pg.KMOD_SHIFT) |
                    (bool(pg.key.get_mods() & pg.KMOD_CTRL) << 1) +
                    self.force_mode.value
                ) % 3
            )

        self.grid.fill_tiles(value, mode, positions, **kwargs)

    def draw_tiles(self, positions: list | set):
        for x, y in positions:
            self.draw_tile(x, y)

    def draw_tile(self, tlx, tly):
        tile = self.grid.tiles[tly][tlx]
        pxpos = tlx * self.tlw, tly * self.tlh

        layer = self.layers[BoardUI.LAYER_COLOR]
        layer.dirty = 1
        Graphics.rect(layer.image, pxpos, self.tile_size, BoardUI.TILE_COLORS[tile.color])

        layer = self.layers[BoardUI.LAYER_NUMBER]
        layer.dirty = 1
        Graphics.rect(layer.image, pxpos, self.tile_size, BoardUI.TILE_COLORS[0])

        if 0 < tile.value < 10:
            text = BoardUI.FONT_VALUE.render(
                str(tile.value), True,
                (255, 0, 0) if tile.highlight else ((140, 160, 160) if tile.locked else (255, 255, 255))
            )
            text = smoothscale(text, (text.get_width() * self.tlw / 64, text.get_height() * self.tlh / 64))
            layer.image.blit(text, (
                pxpos[0] + self.tlw / 2 - text.get_width() / 2,
                pxpos[1] + self.tlh / 2 - text.get_height() / 2
            ))
        elif tile.mark:
            textstr = ''.join(str(i + 1) for i in range(9) if 1 << i & tile.mark)
            text = BoardUI.FONT_MARK.render(textstr, True, (255, 255, 255))
            text = smoothscale(text, (text.get_width() * self.tlw / 64, text.get_height() * self.tlh / 64))
            layer.image.blit(text, (
                pxpos[0] + self.tlw / 2 - text.get_width() / 2,
                pxpos[1] + self.tlh / 2 - text.get_height() / 2
            ))

    def set_title(self, title: str):
        if not len(title):
            title = " "
        self.title.set_text(title.upper())

    def get_tile_pos(self, pxpos: tuple[float, float]) -> tuple[int, int]:
        return int(pxpos[0] / self.tlw), int(pxpos[1] / self.tlh)

    def redraw_rules(self):
        self.layers[BoardUI.LAYER_TOP_RULE].image.fill((0, 0, 0, 0))
        self.layers[BoardUI.LAYER_BOTTOM_RULE].image.fill((0, 0, 0, 0))
        for _ in self.rule_manager.component_rules:
            if isinstance(_, (DotRule, SurroundRule, KillerRule)):
                _.draw(self.layers[BoardUI.LAYER_TOP_RULE].image, self.tile_size)
            else:
                _.draw(self.layers[BoardUI.LAYER_BOTTOM_RULE].image, self.tile_size)
        self.layers[BoardUI.LAYER_TOP_RULE].dirty = 1
        self.layers[BoardUI.LAYER_BOTTOM_RULE].dirty = 1

    def __initdraw(self):
        layer = self.layers[BoardUI.LAYER_GRID]

        for tly in range(9):
            Graphics.line(
                layer.image,
                (0, tly * self.tlh), (self.grid_rect.w, tly * self.tlh),
                1 if tly % 3 else 2, (140, 160, 160)
            )

        for tlx in range(9):
            Graphics.line(
                layer.image,
                (tlx * self.tlw, 0), (tlx * self.tlw, self.grid_rect.h),
                1 if tlx % 3 else 2, (140, 160, 160)
            )

        Graphics.line(
            layer.image,
            (0, self.grid_rect.h - 1), (self.grid_rect.w, self.grid_rect.h - 1),
            2, (140, 160, 160)
        )
        Graphics.line(
            layer.image,
            (self.grid_rect.w - 1, 0), (self.grid_rect.w - 1, self.grid_rect.h),
            2, (140, 160, 160)
        )

