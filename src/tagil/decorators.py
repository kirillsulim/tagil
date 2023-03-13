from tagil.manager import InjectionManager


def component(cls=None):
    if cls is None:
        return lambda c: component(c)

    InjectionManager().register_component(cls)

    return cls
