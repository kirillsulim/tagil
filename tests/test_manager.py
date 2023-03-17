from unittest import TestCase

from tagil import component, InjectionManager, constructor
from tagil.exceptions import *


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


@component(name="named_stub")
class NamedStub:
    pass


@component
class WithNamedStub:
    def __init__(self, named_stub):
        self.named_stub = named_stub


class DuplicatedStab:
    pass


@constructor
def simple_constructor():
    return 1


@constructor
def composite_constructor(simple_constructor):
    return 2 + simple_constructor


class ConstructorReturn:
    pass


@constructor
def returnig_constructor() -> ConstructorReturn:
    return ConstructorReturn()


class Unregistered:
    pass


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

    def test_resolve_by_argument_name(self):
        instance = InjectionManager().get_component(WithNamedStub)

        self.assertTrue(isinstance(instance, WithNamedStub))
        self.assertTrue(isinstance(instance.named_stub, NamedStub))

    def test_simple_constructor(self):
        instance = InjectionManager().get_component(name="simple_constructor")

        self.assertEqual(1, instance)

    def test_composite_constructor(self):
        instance = InjectionManager().get_component(name="composite_constructor")

        self.assertEqual(3, instance)

    def test_raise_exception_when_add_component_with_same_name(self):
        InjectionManager().register_component(DuplicatedStab, name="duplicate")

        with self.assertRaises(DuplicateNameForComponent) as context:
            InjectionManager().register_component(DuplicatedStab, name="duplicate")

        self.assertEqual("Component or constructor with name 'duplicate' already exists.", str(context.exception))

    def test_raise_exception_when_trying_to_get_unregistered_component_by_cls(self):
        with self.assertRaises(NoRegisteredClassFound) as context:
            InjectionManager().get_component(Unregistered)

        self.assertEqual("Cannot find class Unregistered.", str(context.exception))

    def test_get_by_constructor_return_class(self):
        instance = InjectionManager().get_component(ConstructorReturn)

        self.assertTrue(isinstance(instance, ConstructorReturn))
