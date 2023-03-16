# tagil

A simple dependency injection library for python

## Simple usage

To mark class as injectable use `@component` annotation:

```python
from tagil import component

@component
class InjectableClass:
    def __init__(self):
        pass
```

Now you can construct instance of this class with `InjectionManager`:

```python
from tagil import InjectionManager

instance = InjectionManager().get_component(InjectableClass)
```

All dependent instances from `__init__` will be resolved automatically if there is class annotation and `@component` 
decorator:

```python
from tagil import component, InjectionManager

@component
class ClassWithDependency:
    def __init__(self, injectable: InjectableClass):
        self.injectable = injectable

instance = InjectionManager().get_component(ClassWithDependency)
```

Instance will be fully initialized.
