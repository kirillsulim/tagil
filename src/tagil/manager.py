from inspect import signature

from tagil.exceptions import NoRegisteredClassFound
from tagil.singleton import Singleton


class InjectionManager(metaclass=Singleton):
    def __init__(self):
        self.components = {}

    def register_component(self, cls):
        self.components[cls] = None

    def get_component(self, cls):
        if cls in self.components:
            if self.components[cls] is None:
                argument_types = signature(cls.__init__).parameters
                kwargs = {}
                for i, argument in enumerate(argument_types):
                    if i == 0:
                        continue  # Skip self
                    name = argument
                    type = argument_types[argument].annotation
                    kwargs[name] = self.get_component(type)
                self.components[cls] = cls(**kwargs)
            return self.components[cls]
        else:
            raise NoRegisteredClassFound(cls)
