from typing import Callable


class Event:

    def __init__(self):
        self.__handlers: list[Callable] = []

    def add_handler(self, handler: Callable):
        self.__handlers.append(handler)

    def remove_handler(self, handler: Callable):
        self.__handlers.remove(handler)

    def __call__(self, *args, **kwargs):
        for handler in self.__handlers:
            handler(*args, **kwargs)
