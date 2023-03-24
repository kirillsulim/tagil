import inspect
import os
from inspect import signature
from collections import defaultdict
from typing import Optional, Dict, Union, Type, Callable, List
from threading import Lock

from tagil.exceptions import (
    DuplicateNameForComponent,
    ManyComponentsMatches,
    NoRegisteredComponentFound,
)
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
        profile: Optional[Union[str, List[str]]] = None,
    ):
        if cls is None and constructor is None:
            raise ValueError("Expect cls or constructor but both are None")
        elif cls is not None and constructor is not None:
            raise ValueError("Expect clr or constructor but both are not None")

        if constructor is not None:
            cls = _extract_type_from_annotation(
                signature(constructor).return_annotation
            )
            if name is None:
                name = constructor.__name__
        elif cls is not None:
            constructor = cls
        else:
            raise ValueError("Somehow check of constructor or cls presence failed")

        self.cls = cls
        self.constructor = constructor
        self.name = name
        self.inject = {} if inject is None else inject
        self.profile = None if profile is None else set(profile)

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
                        f"Illegal inject direction '{inject_direction}' of type {inject_direction.__class__}."
                    )
            else:
                cls = _extract_type_from_annotation(argument_types[argument].annotation)
                name = argument

            result[argument] = ArgumentData(name, cls)

        return result


class InjectionManager(metaclass=Singleton):
    PROFILES_ENV = "TAGIL_PROFILES"

    def __init__(self):
        self.by_class = defaultdict(list)
        self.by_name = defaultdict(list)
        self.init_stack = []

        self.profiles = self._parse_profiles()

    def register_component(
        self,
        cls: Type,
        name: Optional[str] = None,
        inject: Optional[Dict[str, Union[str, Type]]] = None,
        profile: Optional[Union[str, List[str]]] = None,
    ):
        ic = InstanceContainer(
            cls=cls,
            name=name,
            inject=inject,
            profile=profile,
        )

        self._add_container(ic)

    def register_constructor(
        self,
        method: Callable,
        name: Optional[str] = None,
        inject: Optional[Dict[str, Union[str, Type]]] = None,
        profile: Optional[Union[str, List[str]]] = None,
    ):
        ic = InstanceContainer(
            constructor=method,
            name=name,
            inject=inject,
            profile=profile,
        )

        self._add_container(ic)

    def get_component(self, cls=None, name=None):
        candidates = []
        if cls is not None:
            candidates.extend(self.by_class[cls])
            candidates = list(
                filter(
                    lambda c: c.profile is None
                    or len(c.profile.intersection(self.profiles)) != 0,
                    candidates,
                )
            )
            if len(candidates) > 1 and name is not None:
                candidates = list(filter(lambda ic: ic.name == name, candidates))
        elif name is not None:
            candidates.extend(self.by_name[name])
            candidates = list(
                filter(
                    lambda c: c.profile is None
                    or len(c.profile.intersection(self.profiles)) != 0,
                    candidates,
                )
            )
        else:
            raise ValueError("Must be called with cls or name or both")

        if len(candidates) == 0:
            raise NoRegisteredComponentFound(cls, name)
        elif len(candidates) == 1:
            return self._get_instance(candidates[0])
        else:
            raise ManyComponentsMatches(map(lambda ic: ic.cls, candidates))

    def post_init(self):
        for instance in self.init_stack:
            if self._has_post_init(instance):
                instance.post_init()

    def pre_destroy(self):
        while len(self.init_stack) != 0:
            instance = self.init_stack.pop()
            if self._has_pre_destroy(instance):
                instance.pre_destroy()

    def _get_instance(self, ic: InstanceContainer):
        if ic.instance is not None:
            return ic.instance

        with ic.mutex:
            if ic.instance is None:
                kwargs = {}
                for argument, data in ic.get_arguments_data().items():
                    kwargs[argument] = self.get_component(cls=data.cls, name=data.name)

                ic.instance = ic.constructor(**kwargs)
                self.init_stack.append(ic.instance)
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

    @staticmethod
    def _has_post_init(instance):
        return hasattr(instance, "post_init") and callable(instance.post_init)

    @staticmethod
    def _has_pre_destroy(instance):
        return hasattr(instance, "pre_destroy") and callable(instance.pre_destroy)

    @staticmethod
    def _parse_profiles():
        profiles_str = os.environ.get(InjectionManager.PROFILES_ENV, "")
        return {s.strip().lower() for s in profiles_str.split(",")}
