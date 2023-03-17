import inspect
from inspect import signature
from collections import defaultdict
from typing import Optional
from threading import Lock

from tagil.exceptions import *
from tagil.singleton import Singleton


class InstanceContainer:
    def __init__(self):
        self.name = None
        self.cls = None
        self.constructor = None
        self.instance = None
        self.mutex = Lock()


class InjectionManager(metaclass=Singleton):
    def __init__(self):
        self.by_class = defaultdict(list)
        self.by_name = defaultdict(list)

    def register_component(self, cls, name: Optional[str]):
        ic = InstanceContainer()
        ic.cls = cls
        ic.constructor = cls
        ic.name = name

        self.by_class[cls].append(ic)
        for base in cls.__bases__:
            self.by_class[base].append(ic)

        if name is not None:
            self._add_container_by_name(name, ic)

    def register_constructor(self, method, name: Optional[str] = None):
        ic = InstanceContainer()
        ic.constructor = method

        if name is None:
            name = method.__name__

        ic.name = name

        res = signature(method).return_annotation
        # Todo: add class info

        self._add_container_by_name(name, ic)

    def get_component(self, cls=None, name=None):
        candidates = []
        if cls is not None:
            candidates.extend(self.by_class[cls])
            if len(candidates) > 1 and name is not None:
                candidates = list(filter(lambda ic: ic.name == name, candidates))
        elif name is not None:
            candidates.extend(self.by_name[name])
        else:
            raise ValueError("Must be called with cls or name or both")

        if len(candidates) == 0:
            raise NoRegisteredClassFound(cls)
        elif len(candidates) == 1:
            return self._get_instance(candidates[0])
        else:
            raise ManyComponentsMatches(map(lambda ic: ic.cls, candidates))

    def _get_instance(self, ic: InstanceContainer):
        if ic.instance is not None:
            return ic.instance

        with ic.mutex:
            constructor_function = ic.constructor if ic.constructor is not None else ic.cls.__init__

            argument_types = signature(constructor_function).parameters
            kwargs = {}
            for i, argument in enumerate(argument_types):
                if constructor_function == ic.cls.__init__ and i == 0:
                    continue  # Skip self for __init__
                type = argument_types[argument].annotation
                type = type if type is not inspect._empty else None
                kwargs[argument] = self.get_component(cls=type, name=argument)

        instance = constructor_function(**kwargs)
        ic.instance = instance
        return instance

    def _add_container_by_name(self, name: str, ic: InstanceContainer):
        if name in self.by_name:
            raise DuplicateNameForComponent(name)
        self.by_name[name].append(ic)

    def _add_container_by_class(self, cls, ic: InstanceContainer):
        if cls is object:
            return

        self.by_class[cls].append(ic)
        for base in cls.__bases__:
            self._add_container_by_class(base, ic)
