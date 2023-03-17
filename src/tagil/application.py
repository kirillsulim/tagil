from abc import ABCMeta, abstractmethod
import asyncio

from tagil import InjectionManager


class Application(metaclass=ABCMeta):
    @abstractmethod
    def run(self) -> int:
        """Must be implemented in descendant"""
        pass

    @staticmethod
    def main():
        manager = InjectionManager()
        app_instance = manager.get_component(Application)

        manager.post_init()
        return_code = app_instance.run()
        manager.pre_destroy()

        exit(return_code)


class AsyncApplication(metaclass=ABCMeta):
    @abstractmethod
    async def run(self) -> int:
        """Must be implemented in descendant"""
        pass

    @staticmethod
    def main():
        manager = InjectionManager()
        app_instance = manager.get_component(AsyncApplication)

        manager.post_init()
        return_code = asyncio.run(app_instance.run())
        manager.pre_destroy()

        exit(return_code)
