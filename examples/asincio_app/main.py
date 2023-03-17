import asyncio

from tagil import component, AsyncApplication


@component()
class AsyncGreeter:
    async def greet(self):
        await asyncio.sleep(1)
        return "Hello world!"


@component()
class HelloWorldApp(AsyncApplication):
    def __init__(self, greeter: AsyncGreeter):
        self.greeter = greeter

    async def run(self) -> int:
        results = []
        for i in range(10):
            results.append(self.greeter.greet())

        results = await asyncio.gather(*results)

        for r in results:
            print(r)
        return 0


if __name__ == '__main__':
    HelloWorldApp.main()
