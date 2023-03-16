from unittest import TestCase

from tagil import component, InjectionManager


@component
class StubClass:
    def __init__(self):
        self.value = 1


@component
class ClassWithDependency:
    def __init__(self, stub: StubClass):
        self.stub = stub


class InterfaceClass:
    pass


@component
class ImplementationClass(InterfaceClass):
    name = "implementation"

@component
class WithInterfaceDependency:
    def __init__(self, interface: InterfaceClass):
        self.interface = interface


class TestManager(TestCase):
    def test_stub_class_load(self):
        instance = InjectionManager().get_component(StubClass)

        self.assertTrue(isinstance(instance, StubClass), "Instance is note StubClass")
        self.assertEqual(instance.value, 1, "Value mismatch")

    def test_simple_dependency(self):
        instance = InjectionManager().get_component(ClassWithDependency)

        self.assertTrue(isinstance(instance, ClassWithDependency), "Instance is not ClassWithDependency")
        self.assertTrue(isinstance(instance.stub, StubClass), "Instance field is not StubClass")

    def test_resolve_by_interface(self):
        instance = InjectionManager().get_component(WithInterfaceDependency)

        self.assertTrue(isinstance(instance, WithInterfaceDependency))
        self.assertTrue(isinstance(instance.interface, ImplementationClass))
