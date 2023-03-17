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

```python
from tagil import constructor


class SomeDependency:
    pass


class SomeComponent:
    def __init__(self, dep):
       self.dep = dep

        
@constructor
def some_component(dep: SomeDependency) -> SomeComponent:
    return SomeComponent(dep)
```

Function `some_component` will be added as constructor.
You can get its result by function name (or by decorator parameter `name`) and by class annotation if such annotation
present.
All dependencies from constructor arguments will be resolved the same way they are resolved in `__init__` method.

## Inject directive

In some rare cases you would like to manually set injectable components.
For that case use `inject` parameter of `@component` or `@constructor` decorators:

```python
from tagil import component, constructor


@component(inject={
    "dependency": "dependence_component_name",
})
class SomeComponent:
    def __init__(self, dependency):
        self.dependency = dependency


@constructor(inject={
    "dependency": DependencyClass,
})
def some_constructor(dependency):
    return SomeAnotherComponent(dependency)
```

In that case dependencies will be resolved by they names or classes provided in inject dictionary.

## post_init and pre_destroy

When creating components tagil build initialization stack.
You can manually call `InjectionManager().post_init()` and `InjectionManager().pre_destory()` or use application
template via `Application` base class:

```python
from tagil import component, Application


@component()
class SimpleApp(Application):
    def run(self) -> int:
        return 0


if __name__ == "__main__":
    SimpleApp.main()
```

All calls for `post_init` and `pre_destroy` methods of components will be performed by base class.

## Component resolving algorythm

To define which component should be injected at instance creation tagil performs following set of rules:

1. If injectable component name or class is set via `inject` argument, tagil will search component or constructor with 
   that name or class.
2. If type of argument is present:
   1. Tagil will search component or constructor with this type or with subclass type.
   2. In case of many of candidates tagil will try to use argument name as component or constructor name
3. If no type information or decorator rules are set tagil will search component by argument name.
