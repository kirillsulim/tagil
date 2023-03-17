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

## Constructor decorator

You can assign function as a constructor function for component via `@constructor` decorator:



## Component resolving algorythm

To define which component should be injected at instance creation tagil performs following set of rules:

1. If injectable component name is set via `inject` argument, tagil will search component or constructor with that name. (TBD)
2. If type of argument is present 
   1. Tagil will search component or constructor with this type or with subclass type.
   2. In case of many of candidates tagil will try to use argument name as component or constructor name
3. If no type information or decorator rules are set tagil will search component by argument name.
