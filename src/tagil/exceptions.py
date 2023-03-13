class TagilException(Exception):
    def __init__(self, message):
        super().__init__(message)


class NoRegisteredClassFound(TagilException):
    def __init__(self, cls):
        super().__init__(f"Cannot find class {cls.__name__}")
