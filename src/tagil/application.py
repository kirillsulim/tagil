from abc import ABCMeta, abstractmethod

from tagil import InjectionManager


class Application(metaclass=ABCMeta):
    @abstractmethod
    def run(self) -> int:
        """Must be implemented in descendant"""
        pass

    @staticmethod
    def main():
        app_instance = InjectionManager().get_component(Application)

        return_code = app_instance.run()

        exit(return_code)
