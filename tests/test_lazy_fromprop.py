from autowired import (
    AutowireTo,
    FromProperty,
    LazyAutowireService,
    enable_autowire,
)
from wired import ServiceRegistry
from zope.interface import Interface, implementer


class IFoo(Interface):
    pass


@implementer(IFoo)
class Foo:
    pass


class Baz(LazyAutowireService):
    foo_context = None
    bar_name = None
    foo = AutowireTo(context=FromProperty("foo_context"))
    bar = AutowireTo(name=FromProperty("bar_name"))


def test():
    registry = ServiceRegistry()
    enable_autowire(registry)

    foo_context = Foo()
    foo = object()
    bar = object()
    registry.register_singleton(foo, context=IFoo)
    registry.register_singleton(bar, name="BBAARR")
    registry.register_autowire(
        Baz,
        name="baz",
        namespace={"foo_context": foo_context, "bar_name": "BBAARR"},
    )

    container = registry.create_container()
    baz = container.get(name="baz")
    assert foo is baz.foo
    assert bar is baz.bar
