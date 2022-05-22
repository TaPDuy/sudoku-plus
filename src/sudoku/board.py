import pygame as pg
from pygame.rect import Rect
from pygame import Surface, SRCALPHA
from pygame.font import SysFont
from pygame.transform import smoothscale
from pygame.sprite import LayeredDirty, DirtySprite
from pygame_gui.core import IContainerLikeInterface
from pygame_gui.core.interfaces import IUIManagerInterface

from .grid import Grid, InputMode
from .selection import SelectionGrid
from .rules.rule import RuleManager
from .rules.killer import KillerRule
from .rules.surround import SurroundRule
from .rules.dots import DotRule
from core.gfx.graphics import Graphics
from .title import Title
from .timer import Timer, Time


class Board:
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
            title_height=20,
            show_timer=True
    ):
        # Properties
        self.container = container
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
        self.render_tile_size = self.render_tlw, self.render_tlh = self.tile_size
        self.render_grid_rect = self.grid_rect

        # Components
        self.grid = Grid()
        self.selection = SelectionGrid(Rect(
            self.grid_relative_rect.left - self.tlw / 2,
            self.grid_relative_rect.top - self.tlh / 2,
            self.tlw * 10, self.tlh * 10
        ), self)
        self.rule_manager = RuleManager(self.grid)

        self.title_text = " "
        self.title = Title(self.title_text, Rect(
            (self.grid_rect.left, self.grid_rect.top - title_height),
            (self.grid_rect.w, title_height)
        ), sprite_groups, align_top=False)

        self.timer = Timer(Rect(
            (self.grid_rect.left, self.grid_rect.bottom),
            (self.grid_rect.w, title_height / 2)
        ), sprite_groups, align_left=False, prefix="CURRENT TIME: ")
        self.best_time = Title("BEST TIME: 00:00:00", Rect(
            (self.timer.rect.left, self.timer.rect.bottom),
            (self.timer.rect.w, title_height / 2)
        ), sprite_groups, align_left=False)

        self.ui_manager = manager

        # Control properties
        self.force_mode = InputMode.INPUT_MODE_VALUE
        self.focusable: list[Rect] = [self.grid_rect]
        self.is_focused = False
        self.multi_select = False
        self.should_select = False
        self.enable_highlight = True
        self.locked = False
        self.playing = False

        # Layers
        self.__origin_layers = [Surface(self.render_grid_rect.size, SRCALPHA) for _ in range(5)]
        self.layers = [DirtySprite() for _ in range(6)]

        self.layers[Board.LAYER_COLOR].image = Surface(self.grid_rect.size, SRCALPHA)
        self.layers[Board.LAYER_COLOR].rect = Rect(self.grid_rect)
        sprite_groups.add(self.layers[Board.LAYER_COLOR], layer=Board.LAYER_COLOR)

        self.layers[Board.LAYER_BOTTOM_RULE].image = Surface(self.grid_rect.size, SRCALPHA)
        self.layers[Board.LAYER_BOTTOM_RULE].rect = Rect(self.grid_rect)
        sprite_groups.add(self.layers[Board.LAYER_BOTTOM_RULE], layer=Board.LAYER_BOTTOM_RULE)

        self.layers[Board.LAYER_GRID].image = Surface(self.grid_rect.size, SRCALPHA)
        self.layers[Board.LAYER_GRID].rect = Rect(self.grid_rect)
        sprite_groups.add(self.layers[Board.LAYER_GRID], layer=Board.LAYER_GRID)

        self.layers[Board.LAYER_NUMBER].image = Surface(self.grid_rect.size, SRCALPHA)
        self.layers[Board.LAYER_NUMBER].rect = Rect(self.grid_rect)
        sprite_groups.add(self.layers[Board.LAYER_NUMBER], layer=Board.LAYER_NUMBER)

        self.layers[Board.LAYER_TOP_RULE].image = Surface(self.grid_rect.size, SRCALPHA)
        self.layers[Board.LAYER_TOP_RULE].rect = Rect(self.grid_rect)
        sprite_groups.add(self.layers[Board.LAYER_TOP_RULE], layer=Board.LAYER_TOP_RULE)

        self.layers[Board.LAYER_SELECTION] = self.selection
        sprite_groups.add(self.layers[Board.LAYER_SELECTION], layer=Board.LAYER_SELECTION)

        # Event handlers
        self.grid.on_changed.add_handler(self.rule_manager.update)
        self.grid.on_changed.add_handler(self.draw_tiles)
        self.rule_manager.on_conflict_changed.add_handler(self.grid.highlight_conflicts)

        self.selection.generate_mesh_sprites(.25, (255, 0, 255, 150), 1, (255, 0, 255))
        KillerRule.generate_killer_mesh(self.tile_size)
        self.__initdraw()

    def lock(self):
        if self.playing:
            self.timer.stop()
        self.locked = True

    def unlock(self):
        if self.playing:
            self.timer.start()
        self.locked = False

    def hide_timer(self):
        self.timer.hide()
        self.best_time.hide()

    def resize(self, pxpos: tuple[float, float], pxsize: float, padding: float, title_height=20):

        # Properties
        self.rect = self.relative_rect = Rect(pxpos, (pxsize, pxsize))
        if self.container:
            container_rect = self.container.get_container().get_rect()
            self.rect = Rect(
                (container_rect.x + self.rect.left, container_rect.y + self.rect.top),
                self.rect.size
            )

        # Components' properties
        self.grid_rect = Rect(
            self.rect.left + padding, self.rect.top + padding,
            self.rect.w - padding * 2, self.rect.h - padding * 2
        )
        self.grid_relative_rect = Rect((padding, padding), self.grid_rect.size)
        self.tile_size = self.tlw, self.tlh = self.grid_rect.w / 9, self.grid_rect.h / 9

        # Components
        self.selection.set_relative_rect(Rect(
            self.grid_relative_rect.left - self.tlw / 2,
            self.grid_relative_rect.top - self.tlh / 2,
            self.tlw * 10, self.tlh * 10
        ))
        self.title.set_rect(Rect(
            (self.grid_rect.left, self.grid_rect.top - title_height),
            (self.grid_rect.w, title_height)
        ))
        self.timer.set_rect(Rect(
            (self.grid_rect.left, self.grid_rect.bottom),
            (self.grid_rect.w, title_height / 2)
        ))
        self.best_time.set_rect(Rect(
            (self.timer.rect.left, self.timer.rect.bottom),
            (self.timer.rect.w, title_height / 2)
        ))

        # Layers
        for _ in range(5):
            self.layers[_].dirty = 1
            self.layers[_].rect = self.grid_rect
            self.layers[_].image = smoothscale(self.__origin_layers[_], self.grid_rect.size)

    def set_highscore(self, time: Time):
        self.best_time.set_text("BEST TIME: " + str(time))

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

        self.timer.process_events(evt)

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
        if self.locked:
            return

        if not self.playing:
            self.timer.start()
            self.playing = True

        if not mode:
            mode = InputMode(
                (
                    (pg.key.get_mods() & pg.KMOD_SHIFT) |
                    (bool(pg.key.get_mods() & pg.KMOD_CTRL) << 1) +
                    self.force_mode.value
                ) % 3
            )

        self.grid.fill_tiles(value, mode, positions, **kwargs)

    def set_enable_highlight(self, b: bool):
        self.enable_highlight = b
        self.draw_tiles(set(self.rule_manager.conflicts.keys()))

    def draw_tiles(self, positions: list | set):
        for x, y in positions:
            self.draw_tile(x, y)

    def draw_tile(self, tlx, tly):
        tile = self.grid.tiles[tly][tlx]
        pxpos = tlx * self.render_tlw, tly * self.render_tlh

        layer = self.__origin_layers[Board.LAYER_COLOR]
        Graphics.rect(layer, pxpos, self.render_tile_size, Board.TILE_COLORS[tile.color])
        self.layers[Board.LAYER_COLOR].dirty = 1
        self.layers[Board.LAYER_COLOR].image = smoothscale(layer, self.grid_rect.size)

        layer = self.__origin_layers[Board.LAYER_NUMBER]
        Graphics.rect(layer, pxpos, self.render_tile_size, Board.TILE_COLORS[0])

        if 0 < tile.value < 10:
            text = Board.FONT_VALUE.render(
                str(tile.value), True,
                (255, 0, 0) if self.enable_highlight and tile.highlight else
                ((140, 160, 160) if tile.locked else (255, 255, 255))
            )
            text = smoothscale(text, (text.get_width() * self.render_tlw / 64, text.get_height() * self.render_tlh / 64))
            layer.blit(text, (
                pxpos[0] + self.render_tlw / 2 - text.get_width() / 2,
                pxpos[1] + self.render_tlh / 2 - text.get_height() / 2
            ))
        elif tile.mark:
            textstr = ''.join(str(i + 1) for i in range(9) if 1 << i & tile.mark)
            text = Board.FONT_MARK.render(textstr, True, (255, 255, 255))
            text = smoothscale(text, (text.get_width() * self.render_tlw / 64, text.get_height() * self.render_tlh / 64))
            layer.blit(text, (
                pxpos[0] + self.render_tlw / 2 - text.get_width() / 2,
                pxpos[1] + self.render_tlh / 2 - text.get_height() / 2
            ))

        self.layers[Board.LAYER_NUMBER].dirty = 1
        self.layers[Board.LAYER_NUMBER].image = smoothscale(layer, self.grid_rect.size)

    def set_title(self, title: str):
        self.title_text = title if len(title) else " "
        self.title.set_text(self.title_text.upper())

    def get_tile_pos(self, pxpos: tuple[float, float]) -> tuple[int, int]:
        return int(pxpos[0] / self.tlw), int(pxpos[1] / self.tlh)

    def redraw_rules(self):
        self.__origin_layers[Board.LAYER_TOP_RULE].fill((0, 0, 0, 0))
        self.__origin_layers[Board.LAYER_BOTTOM_RULE].fill((0, 0, 0, 0))
        for _ in self.rule_manager.component_rules:
            if isinstance(_, (DotRule, SurroundRule, KillerRule)):
                _.draw(self.__origin_layers[Board.LAYER_TOP_RULE], self.render_tile_size)
            else:
                _.draw(self.__origin_layers[Board.LAYER_BOTTOM_RULE], self.render_tile_size)

        self.layers[Board.LAYER_TOP_RULE].dirty = 1
        self.layers[Board.LAYER_BOTTOM_RULE].dirty = 1
        self.layers[Board.LAYER_TOP_RULE].image = smoothscale(self.__origin_layers[Board.LAYER_TOP_RULE], self.grid_rect.size)
        self.layers[Board.LAYER_BOTTOM_RULE].image = smoothscale(self.__origin_layers[Board.LAYER_BOTTOM_RULE], self.grid_rect.size)

    def __initdraw(self):
        layer = self.__origin_layers[Board.LAYER_GRID]
        layer.fill((0, 0, 0, 0))

        for tly in range(9):
            Graphics.line(
                layer,
                (0, tly * self.render_tlh), (self.render_grid_rect.w, tly * self.render_tlh),
                1 if tly % 3 else 2, (140, 160, 160)
            )

        for tlx in range(9):
            Graphics.line(
                layer,
                (tlx * self.render_tlw, 0), (tlx * self.render_tlw, self.render_grid_rect.h),
                1 if tlx % 3 else 2, (140, 160, 160)
            )

        Graphics.line(
            layer,
            (0, self.render_grid_rect.h - 1), (self.render_grid_rect.w, self.render_grid_rect.h - 1),
            2, (140, 160, 160)
        )
        Graphics.line(
            layer,
            (self.render_grid_rect.w - 1, 0), (self.render_grid_rect.w - 1, self.render_grid_rect.h),
            2, (140, 160, 160)
        )

        self.layers[Board.LAYER_GRID].dirty = 1
        self.layers[Board.LAYER_GRID].image = smoothscale(layer, self.grid_rect.size)
