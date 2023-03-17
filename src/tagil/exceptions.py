from typing import Iterable


class TagilException(Exception):
    def __init__(self, message):
        super().__init__(message)


class NoRegisteredComponentFound(TagilException):
    def __init__(self, cls, name):
        super().__init__(
            f"Cannot find component by class {cls.__name__} and name '{name}'."
        )


class ManyComponentsMatches(TagilException):
    def __init__(self, classes: Iterable):
        super().__init__(f"Many components matches: {', '.join(map(str, classes))}.")


class DuplicateNameForComponent(TagilException):
    def __init__(self, name: str):
        super().__init__(f"Component or constructor with name '{name}' already exists.")
