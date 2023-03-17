from tagil import component, Application


@component()
class SimpleApp(Application):
    def run(self) -> int:
        return 0


if __name__ == '__main__':
    SimpleApp.main()
