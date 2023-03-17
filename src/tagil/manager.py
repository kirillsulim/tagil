import inspect
from inspect import signature
from collections import defaultdict
from typing import Optional, Dict, Union, Type, Callable
from threading import Lock

from tagil.exceptions import *
from tagil.singleton import Singleton


def _extract_type_from_annotation(annotation) -> Optional[Type]:
    return None if annotation is inspect._empty else annotation


class ArgumentData:
    def __init__(self, name: Optional[str], cls: Optional[Type]):
        self.name = name
        self.cls = cls


class InstanceContainer:
    def __init__(
            self,
            cls: Optional[type] = None,
            constructor: Optional[Callable] = None,
            name: Optional[str] = None,
            inject: Optional[Dict[str, Union[str, Type]]] = None,
    ):
        if cls is None and constructor is None:
            raise ValueError(f"Expect cls or constructor but both are None")
        elif cls is not None and constructor is not None:
            raise ValueError(f"Expect clr or constructor but both are not None")

        if constructor is not None:
            cls = _extract_type_from_annotation(signature(constructor).return_annotation)
            if name is None:
                name = constructor.__name__
        elif cls is not None:
            constructor = cls
        else:
            raise ValueError(f"Somehow check of constructor or cls presence failed")

        self.cls = cls
        self.constructor = constructor
        self.name = name
        self.inject = {} if inject is None else inject

        self.instance = None
        self.mutex = Lock()

    def get_arguments_data(self) -> Dict[str, ArgumentData]:
        result = {}

        argument_types = signature(self.constructor).parameters
        for argument in argument_types:
            if argument in self.inject:
                inject_direction = self.inject[argument]
                if isinstance(inject_direction, str):
                    name = inject_direction
                    cls = None
                elif isinstance(inject_direction, Type):
                    name = None
                    cls = inject_direction
                else:
                    raise ValueError(
                        f"Illegal inject direction '{inject_direction}' of type {inject_direction.__class__}.")
            else:
                cls = _extract_type_from_annotation(argument_types[argument].annotation)
                name = argument

            result[argument] = ArgumentData(name, cls)

        return result


class InjectionManager(metaclass=Singleton):
    def __init__(self):
        self.by_class = defaultdict(list)
        self.by_name = defaultdict(list)

    def register_component(
            self,
            cls: Type,
            name: Optional[str] = None,
            inject: Optional[Dict[str, Union[str, Type]]] = None
    ):
        ic = InstanceContainer(
            cls=cls,
            name=name,
            inject=inject
        )

        self._add_container(ic)

    def register_constructor(
            self,
            method: Callable,
            name: Optional[str] = None,
            inject: Optional[Dict[str, Union[str, Type]]] = None
    ):
        ic = InstanceContainer(
            constructor=method,
            name=name,
            inject=inject,
        )

        self._add_container(ic)

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
            if ic.instance is None:
                kwargs = {}
                for argument, data in ic.get_arguments_data().items():
                    kwargs[argument] = self.get_component(cls=data.cls, name=data.name)

                ic.instance = ic.constructor(**kwargs)
            return ic.instance

    def _add_container(self, ic: InstanceContainer):
        if ic.name is not None:
            self._add_container_by_name(ic.name, ic)

        if ic.cls is not None:
            self._add_container_by_class(ic.cls, ic)

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