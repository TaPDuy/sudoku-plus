from typing import Callable
import inspect


# class EventData:
#     def __init__(self, **data):
#         self.__data = data
#
#     @property
#     def args(self):
#         return list(self.__data.keys())
#
#     @property
#     def param(self):
#         return list(self.__data.values())
#
#     def __getitem__(self, name):
#         return self.__data[name]


class Event:

    def __init__(self):
        self.__handlers: list[Callable] = []

    def add_handler(self, handler: Callable):
        self.__handlers.append(handler)

    def remove_handler(self, handler: Callable):
        self.__handlers.remove(handler)

    def __call__(self, **data):
        for handler in self.__handlers:
            param = inspect.signature(handler).parameters.values()
            required_args = {p.name for p in param if p.default is p.empty}
            if required_args.issubset(set(data)):
                handler(*[data[p.name] for p in param if p.name in data])
