from pygame.event import custom_type
from pygame.time import set_timer
from pygame.sprite import LayeredDirty
from pygame.rect import Rect

from .title import Title


TIMER_TICK = custom_type()
set_timer(TIMER_TICK, 1000)


class Time:

    def __init__(self, hours=0, minutes=0, seconds=0):
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds

        if self.ticks < 0:
            self.hours = self.minutes = self.seconds = 0
        else:
            self.__normalize()

    @classmethod
    def to_time(cls, ticks: int):
        return cls(seconds=ticks)

    @property
    def ticks(self) -> int:
        return self.hours * 3600 + self.minutes * 60 + self.seconds

    def __iadd__(self, other: int):
        self.seconds += other
        self.__normalize()

        return self

    def __isub__(self, other: int):
        if self.ticks < other:
            self.hours = self.minutes = self.seconds = 0
        else:
            self.seconds -= other
            self.__normalize()

        return self

    def __normalize(self):
        if self.seconds < 0 or self.seconds >= 60:
            self.minutes += self.seconds // 60
            self.seconds %= 60
        if self.minutes < 0 or self.minutes >= 60:
            self.hours += self.minutes // 60
            self.minutes %= 60

    def __lt__(self, other):
        if self.hours != other.hours:
            return self.hours < other.hours
        elif self.minutes != other.minutes:
            return self.minutes < other.minutes
        else:
            return self.seconds < other.seconds

    def __le__(self, other):
        if self.hours != other.hours:
            return self.hours < other.hours
        elif self.minutes != other.minutes:
            return self.minutes < other.minutes
        else:
            return self.seconds <= other.seconds

    def __gt__(self, other):
        if self.hours != other.hours:
            return self.hours > other.hours
        elif self.minutes != other.minutes:
            return self.minutes > other.minutes
        else:
            return self.seconds > other.seconds

    def __ge__(self, other):
        if self.hours != other.hours:
            return self.hours > other.hours
        elif self.minutes != other.minutes:
            return self.minutes > other.minutes
        else:
            return self.seconds >= other.seconds

    def __eq__(self, other):
        return self.hours == other.hours and self.minutes == other.minutes and self.seconds == other.seconds

    def __ne__(self, other):
        return self.hours != other.hours or self.minutes != other.minutes or self.seconds != other.seconds

    def __str__(self):
        return f"{self.hours:02d}:{self.minutes:02d}:{self.seconds:02d}"

    def __repr__(self):
        return f"Time={{ticks={self.ticks}, hrs={self.hours}, min={self.minutes}, sec={self.seconds}}}"


class Timer(Title):

    def __init__(self, rect: Rect, sprite_groups: LayeredDirty, align_top=True, align_left=True, prefix=""):
        super().__init__(prefix + "00:00:00", rect, sprite_groups, align_top, align_left)
        self.time: Time = Time()
        self.running = False
        self.prefix = prefix

    def start(self):
        self.running = True

    def stop(self):
        self.running = False

    def reset(self) -> Time:
        tmp = self.time
        self.time = Time()
        return tmp

    def process_events(self, evt):
        if evt.type == TIMER_TICK:
            if self.running:
                self.time += 1
                self.set_text(self.prefix + str(self.time))
