from autowired import AutowireTo, LazyAutowireService, enable_autowire
from wired import ServiceRegistry
from zope.interface import Interface


class IFoo(Interface):
    pass


class IBar(Interface):
    pass


class IBaz(Interface):
    pass


class Baz(LazyAutowireService):
    foo = AutowireTo(IFoo)
    bar = AutowireTo(IBar)


def test():
    registry = ServiceRegistry()
    enable_autowire(registry)

    foo = object()
    bar = object()
    registry.register_singleton(foo, IFoo)
    registry.register_singleton(bar, IBar)
    registry.register_autowire(Baz, IBaz)

    container = registry.create_container()
    baz = container.get(IBaz)

    assert "foo" not in baz.__dict__
    assert foo is baz.foo
    assert "foo" in baz.__dict__

    assert "bar" not in baz.__dict__
    assert bar is baz.bar
    assert "bar" in baz.__dict__
