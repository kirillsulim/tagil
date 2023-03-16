from inspect import signature
from collections import defaultdict

from tagil.exceptions import NoRegisteredClassFound, ManyComponentsMatches
from tagil.singleton import Singleton


class InstanceContainer:
    def __init__(self):
        self.name = None
        self.cls = None
        self.constructor = None
        self.instance = None

class InjectionManager(metaclass=Singleton):
    def __init__(self):
        self.by_class = defaultdict(list)

    def register_component(self, cls):
        ic = InstanceContainer()
        ic.cls = cls
        ic.constructor = cls

        self.by_class[cls].append(ic)

        for base in cls.__bases__:
            self.by_class[base].append(ic)

    def get_component(self, cls):
        candidates = self.by_class[cls]
        if len(candidates) == 0:
            raise NoRegisteredClassFound(cls)
        elif len(candidates) == 1:
            return self._get_instance(candidates[0])
        else:
            raise ManyComponentsMatches(map(lambda ic: ic.cls, candidates))

    def _get_instance(self, ic: InstanceContainer):
        if ic.instance is not None:
            return ic.instance

        constructor_function = ic.constructor if ic.constructor is not None else ic.cls.__init__

        argument_types = signature(constructor_function).parameters
        kwargs = {}
        for i, argument in enumerate(argument_types):
            if constructor_function == ic.cls.__init__ and i == 0:
                continue  # Skip self for __init__
            name = argument
            type = argument_types[argument].annotation
            kwargs[name] = self.get_component(type)

        instance = constructor_function(**kwargs)
        ic.instance = instance
        return instance
