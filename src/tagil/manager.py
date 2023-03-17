import inspect
from inspect import signature
from collections import defaultdict
from typing import Optional, Dict, Union, Type
from threading import Lock

from tagil.exceptions import *
from tagil.singleton import Singleton


class InstanceContainer:
    def __init__(self):
        self.name = None
        self.cls = None
        self.constructor = None
        self.inject = None
        self.instance = None
        self.mutex = Lock()


class InjectionManager(metaclass=Singleton):
    def __init__(self):
        self.by_class = defaultdict(list)
        self.by_name = defaultdict(list)

    def register_component(self, cls, name: Optional[str] = None, inject: Optional[Dict[str, Union[str, Type]]] = None):
        ic = InstanceContainer()
        ic.cls = cls
        ic.name = name
        if inject is not None:
            ic.inject = inject
        else:
            ic.inject = {}

        self.by_class[cls].append(ic)
        for base in cls.__bases__:
            self.by_class[base].append(ic)

        if name is not None:
            self._add_container_by_name(name, ic)

    def register_constructor(self, method, name: Optional[str] = None, inject: Optional[Dict[str, Union[str, Type]]] = None):
        ic = InstanceContainer()
        ic.constructor = method
        if inject is not None:
            ic.inject = inject
        else:
            ic.inject = {}

        if name is None:
            name = method.__name__

        ic.name = name

        res = signature(method).return_annotation
        if res is not inspect._empty:
            self._add_container_by_class(res, ic)

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
            raise NoRegisteredComponentFound(cls, name)
        elif len(candidates) == 1:
            return self._get_instance(candidates[0])
        else:
            raise ManyComponentsMatches(map(lambda ic: ic.cls, candidates))

    def _get_instance(self, ic: InstanceContainer):
        if ic.instance is not None:
            return ic.instance

        with ic.mutex:
            constructor_function = ic.constructor if ic.constructor is not None else ic.cls

            argument_types = signature(constructor_function).parameters
            kwargs = {}
            for argument in argument_types:
                type = argument_types[argument].annotation
                type = type if type is not inspect._empty else None
                name = argument
                if argument in ic.inject:
                    inject_direction = ic.inject[argument]
                    if isinstance(inject_direction, str):
                        name = inject_direction
                        type = None
                    elif isinstance(inject_direction, Type):
                        type = inject_direction
                    else:
                        raise ValueError(f"Illegal inject direction '{inject_direction}' of type {inject_direction.__class__}.")

                kwargs[argument] = self.get_component(cls=type, name=name)

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
