import os
import random
import numpy as np
import pickle
import json
from datetime import datetime

from pygame import Rect
from pygame_gui.core.interfaces import IUIManagerInterface
from pygame_gui.elements import UIPanel, UISelectionList

from .rules.rule import Rule
from .rules.global_rules import SudokuRule
from core.event import Event
from core.ui import ButtonGrid


def generate_level_id() -> str:
    current_dt = datetime.now()
    return (f"untitled_level"
            f"_{current_dt.hour:02d}{current_dt.minute:02d}{current_dt.second:02d}"
            f"_{current_dt.day:02d}{current_dt.month:02d}{current_dt.year:04d}")


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
    LEVELS_PATH = "data/levels"

    def __init__(self, relative_rect: Rect, manager: IUIManagerInterface, container=None):
        super().__init__(relative_rect, 0, manager, container=container)
        self.levels = []
        self.level_list = UISelectionList(
            Rect(0, 0, self.relative_rect.w, self.relative_rect.h - 30),
            [], manager, container=self
        )

        self.buttons = ButtonGrid((2, 1), Rect(
            self.level_list.relative_rect.bottomleft, (self.relative_rect.w, 30)
        ), 5, manager, self)
        self.buttons.add_button("Load", "load")
        self.buttons.add_button("New", "new")

        # Events
        self.on_load_requested = Event()
        self.buttons.on_button_pressed.add_handler(self.handle_button_pressed)

    def set_relative_rect(self, rect: Rect):
        self.level_list.set_relative_position((0, 0))
        self.level_list.set_dimensions((rect.w, rect.h - 30))

        self.buttons.set_relative_rect(Rect(
            self.level_list.relative_rect.bottomleft, (rect.w, 30)
        ))

        self.set_relative_position(rect.topleft)
        self.set_dimensions(rect.size)

    def load_levels(self):
        filenames = [_ for _ in os.listdir(LevelList.LEVELS_PATH) if _.endswith('.dat')]

        for name in filenames:
            with open(f"{LevelList.LEVELS_PATH}/{name}", 'rb') as f:
                self.levels += [(name, pickle.load(f))]

        self.level_list.set_item_list([_[1].name for _ in self.levels])

    def handle_button_pressed(self, button_id: str):
        match button_id:
            case "load":
                index = -1
                for item in self.level_list.item_list:
                    if item['selected']:
                        index = self.level_list.item_list.index(item)
                        break

                if index != -1:
                    self.on_load_requested(level_id=self.levels[index][0], level=self.levels[index][1])

            case "new":
                self.on_load_requested(level=random_sudoku())


__DEFAULT_SEED = "___bf_g_a|fh__g__i_|ai___de__|hb_a___d_|__df_bi__|_e___c_bh|__ic___gd|_d__e__cf|g_c_ah___"
__SEEDS_PATH = "data/levels/seeds.json"


def load_seeds():
    if os.path.exists(__SEEDS_PATH):
        with open(__SEEDS_PATH, "r") as file:
            tmp = json.load(file)
            print(
                f"[Levels]: Loaded {len(tmp)} level seed(s)." if len(tmp)
                else f"Unable to load level seeds. Using default seed."
            )
            return tmp


seeds = load_seeds() or []


def random_sudoku() -> Level:
    values = [_ for _ in range(1, 10)]
    random.shuffle(values)
    charmap = {chr(ord('a') + _): values[_] for _ in range(9)}

    seed = random.choice(seeds) if len(seeds) else __DEFAULT_SEED
    print(f"[Levels]: Generated level from seed '{seed}'.")

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
