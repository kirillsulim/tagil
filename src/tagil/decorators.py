from typing import Dict

from tagil.manager import InjectionManager


def component(
    cls=None,
    *,
    name: str = None,
    inject: Dict[str, str] = None,
):
    if cls is None:
        return lambda c: component(c, name=name, inject=inject)

    InjectionManager().register_component(cls, name)

    return cls


def constructor(
    method=None,
    *,
    name: str = None,
    inject: Dict[str, str] = None,
):
    if method is None:
        return lambda m: constructor(m, name=name, inject=inject)

    InjectionManager().register_constructor(method, name)
