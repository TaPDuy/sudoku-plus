from pygame.rect import Rect
from pygame_gui.elements import UIPanel, UIButton
from pygame_gui.core.interfaces import IUIManagerInterface
import pygame_gui as pgui

from core.ui import CheckBox
from core.audio import BgmPlayer
from core.event import Event


class SettingsPanel(UIPanel):

    def __init__(self, rect: Rect, manager: IUIManagerInterface, container=None):
        super().__init__(
            rect, 0, manager, container=container,
            margins={'left': 0, 'right': 0, 'top': 0, 'bottom': 0}
        )

        self.pad = 5
        self.component_height = 30

        self.__settings_values = {}
        self.__settings = {}

        self.apply_btn = UIButton(Rect(
            0, 0, self.rect.w - 2 * self.pad, self.component_height
        ), "Apply", self.ui_manager, self)

        self.player = BgmPlayer(rect, self.ui_manager, self)
        self.player.load_bgm()
        self.player.play()

        self.on_changed = Event()

    def process_event(self, evt):
        if evt.type == pgui.UI_BUTTON_PRESSED:
            if evt.ui_element is self.apply_btn:
                changed = {}
                for setting_id in self.__settings:
                    if self.__settings[setting_id].checked != self.__settings_values[setting_id]:
                        changed[setting_id] = self.__settings[setting_id].checked
                        self.__settings_values[setting_id] = self.__settings[setting_id].checked
                self.on_changed(changes=changed)

    def discard_changes(self):
        for setting_id in self.__settings:
            self.__settings[setting_id].set_checked(self.__settings_values[setting_id])

    def add_setting(self, name: str, setting_id: str, initial_value=False):
        ln = len(self.__settings)

        self.__settings_values[setting_id] = initial_value
        self.__settings[setting_id] = CheckBox(Rect(
            self.pad, ln * self.component_height + (ln + 1) * self.pad,
            self.rect.w, self.component_height
        ), name, self.ui_manager, self)
        self.__settings[setting_id].set_checked(initial_value)
        ln += 1

        self.apply_btn.set_relative_position((self.pad, ln * self.pad + ln * self.component_height))

        self.player.set_relative_rect(Rect(
            0, self.apply_btn.relative_rect.bottom,
            self.rect.w, self.rect.h - self.apply_btn.relative_rect.bottom
        ))

    def set_relative_rect(self, rect: Rect):
        i = 0
        for setting in self.__settings.values():
            setting.set_relative_rect(Rect(
                self.pad, i * self.component_height + (i + 1) * self.pad,
                rect.w, self.component_height
            ))
            i += 1

        self.apply_btn.set_relative_position((self.pad, i * self.pad + i * self.component_height))
        self.apply_btn.set_dimensions((rect.w - 2 * self.pad, self.component_height))

        self.player.set_relative_rect(Rect(
            0, self.apply_btn.relative_rect.bottom,
            rect.w, rect.h - self.apply_btn.relative_rect.bottom
        ))

        self.set_relative_position(rect.topleft)
        self.set_dimensions(rect.size)
