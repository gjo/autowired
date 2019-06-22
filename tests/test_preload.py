from autowired import AutowireTo, enable_autowire
from wired import ServiceRegistry
from zope.interface import Interface


class IFoo(Interface):
    pass


class IBar(Interface):
    pass


class Bar:
    foo = AutowireTo(IFoo)

    def __init__(self, foo):
        self.foo = foo


def test():
    assert isinstance(Bar.foo, AutowireTo)

    registry = ServiceRegistry()
    enable_autowire(registry)

    foo = object()
    registry.register_singleton(foo, IFoo)
    registry.register_autowire(Bar, IBar)

    container = registry.create_container()
    bar = container.get(IBar)
    assert "wired_container" not in bar.__dict__
    assert foo is bar.foo
