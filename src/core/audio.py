import os

import pygame.mixer
import pygame_gui as pgui
from pygame.mixer import Sound
from pygame import Rect
from pygame_gui.core.interfaces import IUIManagerInterface
from pygame_gui.elements import UIPanel, UIButton, UITextBox, UIHorizontalSlider

pygame.mixer.init()


class BgmPlayer(UIPanel):

    def __init__(self, relative_rect: Rect, manager: IUIManagerInterface, container=None):
        super().__init__(relative_rect, 0, manager, container=container)

        self.names = UITextBox("", Rect(0, 0, relative_rect.w, relative_rect.h - 60), manager, container=self)
        self.prev_btn = UIButton(
            Rect(self.names.relative_rect.bottomleft, (self.relative_rect.w / 2, 30)),
            "<<", manager, self
        )
        self.next_btn = UIButton(
            Rect(self.prev_btn.relative_rect.topright, (self.relative_rect.w / 2, 30)),
            ">>", manager, self
        )
        self.volume_btn = UIButton(
            Rect(self.prev_btn.relative_rect.bottomleft, (30, 30)),
            "vol", manager, self
        )
        self.volume_slider = UIHorizontalSlider(
            Rect(self.volume_btn.relative_rect.topright, (self.relative_rect.w - 30, 30)),
            .75, (0.0, 1.0), manager, self
        )
        self.volume_slider.enable_arrow_buttons = False
        self.volume_slider.rebuild()

        self.bgms = ()
        self.__index: int = 0
        self.__prev_volume = 1.0

    def set_relative_rect(self, rect: Rect):
        self.names.set_relative_position((0, 0))
        self.names.set_dimensions((rect.w, rect.h - 60))

        self.prev_btn.set_relative_position(self.names.relative_rect.bottomleft)
        self.prev_btn.set_dimensions((rect.w / 2, 30))

        self.next_btn.set_relative_position(self.prev_btn.relative_rect.topright)
        self.next_btn.set_dimensions((rect.w / 2, 30))

        self.volume_btn.set_relative_position(self.prev_btn.relative_rect.bottomleft)
        self.volume_btn.set_dimensions((30, 30))

        self.volume_slider.set_relative_position(self.volume_btn.relative_rect.topright)
        self.volume_slider.set_dimensions((rect.w - 30, 30))

        self.set_relative_position(rect.topleft)
        self.set_dimensions(rect.size)

    def load_bgm(self):
        filenames = [_ for _ in os.listdir("bgm") if _.endswith(('.mp3', '.wav', '.ogg'))]

        bgms = []
        for name in filenames:
            bgms += [(name, Sound("bgm/" + name))]

        self.bgms = tuple(bgms)

    def play(self):
        self.bgms[self.__index][1].play(loops=-1)
        self.__update_text()

    def stop(self):
        self.bgms[self.__index][1].stop()

    def next(self):
        if len(self.bgms) > 0:
            self.stop()
            self.__index = (self.__index + 1) % len(self.bgms)
            self.set_volume(self.volume_slider.get_current_value())
            self.play()

    def prev(self):
        if len(self.bgms) > 0:
            self.stop()
            self.__index = (self.__index - 1) % len(self.bgms)
            self.set_volume(self.volume_slider.get_current_value())
            self.play()

    def set_volume(self, value):
        self.bgms[self.__index][1].set_volume(value)

    def __update_text(self):
        self.names.set_text(f"Now playing:<br><p>{self.bgms[self.__index][0]}</p>")

    def process_event(self, evt):
        match evt.type:
            case pgui.UI_HORIZONTAL_SLIDER_MOVED:
                self.set_volume(self.volume_slider.get_current_value())
            case pgui.UI_BUTTON_PRESSED:
                match evt.ui_element:
                    case self.volume_btn:
                        if self.volume_slider.get_current_value() != 0.0:
                            self.__prev_volume = self.volume_slider.get_current_value()
                            self.volume_slider.set_current_value(0.0)
                        else:
                            self.volume_slider.set_current_value(self.__prev_volume)

                        self.set_volume(self.volume_slider.get_current_value())
                    case self.prev_btn:
                        self.prev()
                    case self.next_btn:
                        self.next()

