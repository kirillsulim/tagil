from typing import Dict, Union, Type, Optional

from tagil.manager import InjectionManager


def component(
    cls=None,
    *,
    name: str = None,
    inject: Optional[Dict[str, Union[str, Type]]] = None,
):
    if cls is None:
        return lambda c: component(c, name=name, inject=inject)

    InjectionManager().register_component(cls, name, inject)

    return cls


def constructor(
    method=None,
    *,
    name: str = None,
    inject: Optional[Dict[str, Union[str, Type]]] = None,
):
    if method is None:
        return lambda m: constructor(m, name=name, inject=inject)

    InjectionManager().register_constructor(method, name, inject)
