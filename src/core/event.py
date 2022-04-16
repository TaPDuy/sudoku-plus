from typing import Callable
import inspect


class EventData:
    def __init__(self, data: dict[str, object]):
        self.__data = data

    def __getitem__(self, name):
        return self.__data[name]


class Event:

    def __init__(self):
        self.__handlers: list[Callable] = []

    def add_handler(self, handler: Callable):
        self.__handlers.append(handler)

    def remove_handler(self, handler: Callable):
        self.__handlers.remove(handler)

    def __call__(self, data: EventData):
        for handler in self.__handlers:
            handler(*[data[arg] for arg in inspect.signature(handler).parameters.keys()])

