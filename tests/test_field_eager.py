from autowired import AutowireField, FromNamespace, enable_autowire
from wired import ServiceRegistry
from zope.interface import Interface


class Iface00(Interface):
    pass


class Ctxt:
    pass


class IFoo(Interface):
    pass


class Foo:
    impl00 = AutowireField(Iface00)
    impl01 = AutowireField(name="impl01")
    impl02 = AutowireField(name=FromNamespace(name="n_impl02"))
    impl03 = AutowireField(context=FromNamespace(name="n_impl03"))


def test():
    assert isinstance(Foo.impl00, AutowireField)
    assert isinstance(Foo.impl01, AutowireField)
    assert isinstance(Foo.impl02, AutowireField)
    assert isinstance(Foo.impl03, AutowireField)

    registry = ServiceRegistry()
    enable_autowire(registry)

    impl00 = object()
    impl01 = object()
    impl02 = object()
    impl03 = object()

    registry.register_singleton(impl00, Iface00)
    registry.register_singleton(impl01, name="impl01")
    registry.register_singleton(impl02, name="r_impl02")
    registry.register_singleton(impl03, context=Ctxt)
    registry.register_autowire(
        Foo,
        IFoo,
        namespace=dict(n_impl02="r_impl02", n_impl03=Ctxt()),
        lazy=False,
    )

    container = registry.create_container()
    foo = container.get(IFoo)
    assert foo.impl00 is impl00
    assert foo.impl01 is impl01
    assert foo.impl02 is impl02
    assert foo.impl03 is impl03
