from pygame.rect import Rect
from pygame.sprite import DirtySprite, LayeredDirty
from pygame.font import SysFont, Font
from pygame.transform import smoothscale


class Title:

    def __init__(self, text: str, rect: Rect, sprite_groups: LayeredDirty, align_top=True, align_left=True):
        self.rect = rect
        self.align_top = align_top
        self.align_left = align_left

        self.__color = (255, 255, 255)
        self.__font = SysFont("Arial", 64)
        self.__base_sprite = self.__font.render(text, True, self.__color)

        self.__text_sprite = DirtySprite(sprite_groups)
        self.__redraw()

    def set_rect(self, rect: Rect):
        self.rect = rect
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
        width = self.__base_sprite.get_width() * height / self.__base_sprite.get_height()
        self.__text_sprite.rect = Rect(
            (
                self.rect.left if self.align_left else self.rect.right - width,
                self.rect.top if self.align_top else self.rect.bottom - height
            ), (width, height)
        )
        self.__text_sprite.image = smoothscale(self.__base_sprite, self.__text_sprite.rect.size)
