from tagil import component, Application


@component()
class Greeter:
    def greet(self):
        print("Hello world!")

    def post_init(self):
        print("Greeter:post_init")

    def pre_destroy(self):
        print("Greeter:pre_destroy")


@component()
class InitDestroyApp(Application):
    def __init__(self, greeter: Greeter):
        self.greeter = greeter

    def run(self) -> int:
        self.greeter.greet()
        return 0

    def post_init(self):
        print("App:post_init")

    def pre_destroy(self):
        print("App:pre_destroy")


if __name__ == '__main__':
    InitDestroyApp.main()
