from autowired import AutowireTo, LazyAutowireService, enable_autowire
from wired import ServiceRegistry
from zope.interface import Interface


class IFoo(Interface):
    pass


class Foo(LazyAutowireService):
    bar = AutowireTo(name="bar")


def test():
    registry = ServiceRegistry()
    enable_autowire(registry)

    bar = object()
    registry.register_autowire(Foo, IFoo)
    registry.register_singleton(bar, name="bar")

    container = registry.create_container()
    foo = container.get(IFoo)
    assert bar is foo.bar
