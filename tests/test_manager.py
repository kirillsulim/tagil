from unittest import TestCase

from tagil.decorators import component
from tagil.manager import InjectionManager


@component
class StubClass:
    def __init__(self):
        self.value = 1


class TestManager(TestCase):
    def test_stub_class_load(self):
        instance = InjectionManager().get_component(StubClass)

        self.assertTrue(isinstance(instance, StubClass), "Instance is note StubClass")
        self.assertEqual(instance.value, 1, "Value mismatch")
