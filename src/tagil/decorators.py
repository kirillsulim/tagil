from typing import Dict, Union, Type, Optional, List

from tagil.manager import InjectionManager


def component(
    cls=None,
    *,
    name: str = None,
    inject: Optional[Dict[str, Union[str, Type]]] = None,
    profile: Optional[Union[str, List[str]]] = None,
):
    if cls is None:
        return lambda c: component(c, name=name, inject=inject, profile=profile)

    InjectionManager().register_component(cls, name, inject, profile=profile)

    return cls


def constructor(
    method=None,
    *,
    name: str = None,
    inject: Optional[Dict[str, Union[str, Type]]] = None,
    profile: Optional[Union[str, List[str]]] = None,
):
    if method is None:
        return lambda m: constructor(m, name=name, inject=inject, profile=profile)

    InjectionManager().register_constructor(method, name, inject)
