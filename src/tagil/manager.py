from tagil.singleton import Singleton


class InjectionManager(metaclass=Singleton):
    def __init__(self):
        self.components = {}

    def register_component(self, cls):
        self.components[cls] = None

    def get_component(self, cls):
        if cls in self.components:
            if self.components[cls] is None:
                self.components[cls] = cls()
            return self.components[cls]
        else:
            raise NoRegisteredClassFound(cls)
