from tagil import component, Application


@component()
class Greeter:
    def greet(self):
        print("Hello world!")


@component()
class HelloWorldApp(Application):
    def __init__(self, greeter: Greeter):
        self.greeter = greeter

    def run(self) -> int:
        self.greeter.greet()
        return 0


if __name__ == '__main__':
    HelloWorldApp.main()
