import os
import random
import numpy as np
import pickle

import pygame_gui as pgui
from pygame import Rect
from pygame_gui.core.interfaces import IUIManagerInterface
from pygame_gui.elements import UIPanel, UISelectionList, UIButton

from .rules.rule import Rule
from .rules.global_rules import SudokuRule
from core.event import Event


class Level:

    def __init__(self, name="Untitled level", ruleset: set[Rule] = None, start_values: dict[tuple[int, int], int] = None):
        """
        A class that holds all the data needed to load a level.
        :param ruleset: Ruleset that determines winning conditions
        :param start_values: Initial clues - dict[(tile_x, tile_y): value]
        """
        self.__name = name
        self.__ruleset = ruleset or set()
        self.__start_values = start_values or {}

    @property
    def name(self):
        return self.__name

    @property
    def ruleset(self):
        return self.__ruleset

    @property
    def start_values(self):
        return self.__start_values


class LevelList(UIPanel):

    def __init__(self, relative_rect: Rect, manager: IUIManagerInterface, container=None):
        super().__init__(relative_rect, 0, manager, container=container)
        self.levels = ()
        self.level_list = UISelectionList(
            Rect(0, 0, self.relative_rect.w, self.relative_rect.h - 30),
            [], manager, container=self
        )
        self.load_btn = UIButton(
            Rect(self.level_list.relative_rect.bottomleft, (self.relative_rect.w / 2, 30)),
            "Load", manager, self
        )
        self.new_btn = UIButton(
            Rect(self.load_btn.relative_rect.topright, (self.relative_rect.w / 2, 30)),
            "New", manager, self
        )

        # Events
        self.on_load_requested = Event()

    def load_levels(self):
        filenames = [_ for _ in os.listdir("levels") if _.endswith('.dat')]

        lvls = []
        for name in filenames:
            with open("levels/" + name, 'rb') as f:
                lvls += [pickle.load(f)]

        self.levels = tuple(lvls)
        self.level_list.set_item_list([_.name for _ in self.levels])

    def process_event(self, evt):
        match evt.type:
            case pgui.UI_BUTTON_PRESSED:
                match evt.ui_element:
                    case self.load_btn:

                        index = -1
                        for item in self.level_list.item_list:
                            if item['selected']:
                                index = self.level_list.item_list.index(item)
                                break

                        if index != -1:
                            self.on_load_requested(level=self.levels[index])
                    case self.new_btn:
                        self.on_load_requested(level=random_sudoku())


SEEDS = (
    "___bf_g_a|fh__g__i_|ai___de__|hb_a___d_|__df_bi__|_e___c_bh|__ic___gd|_d__e__cf|g_c_ah___",
    "a__dhi__f|gc_____d_|_____abie|__gab_f__|e__g_c__h|__f_ieg__|iadf_____|_b_____cg|h__eab__d",
    "_b_f_h___|eh___ig__|____d____|cg____e__|f_______d|__h____ac|____b____|__ih___cf|___c_f_i_",
    "___f__d__|g____cf__|____ia_h_|_________|_e_ah___c|___c_f_de|_d_b___f_|i_c______|_b____a__",
    "b__c_____|h_d_fb__c|_ach__b__|____b_ci_|e_g___fba|_cb__f___|_b___iad_|f_abe_h_i|_____a__b",
    "_b_______|___f____c|_gd_h____|_____c__b|_h__d__a_|f__e_____|____a_gh_|e____i___|_______d_"
)


def random_sudoku() -> Level:
    values = [_ for _ in range(1, 10)]
    random.shuffle(values)
    charmap = {chr(ord('a') + _): values[_] for _ in range(9)}

    seed = random.choice(SEEDS)
    print(f"Generating level from seed '{seed}'")

    chars = np.array([list(_) for _ in seed.split('|')])
    for _ in np.arange(random.randint(0, 3)):
        chars = np.rot90(chars)

    if random.getrandbits(1):
        chars = np.flip(chars, random.randint(0, 1))

    return Level(
        "Random level",
        {SudokuRule()},
        {(x, y): charmap[chars[y][x]] for y in range(9) for x in range(9) if chars[y][x] != '_'}
    )
