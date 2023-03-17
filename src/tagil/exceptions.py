from typing import List, Iterable


class TagilException(Exception):
    def __init__(self, message):
        super().__init__(message)


class NoRegisteredClassFound(TagilException):
    def __init__(self, cls):
        super().__init__(f"Cannot find class {cls.__name__}.")


class ManyComponentsMatches(TagilException):
    def __init__(self, classes: Iterable):
        super().__init__(f"Many components matches: {', '.join(classes)}.")


class DuplicateNameForComponent(TagilException):
    def __init__(self, name: str):
        super().__init__(f"Component or constructor with name {name} already exists.")
