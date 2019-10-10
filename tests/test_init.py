from autowired import Autowire, AutowireInit, FromNamespace, enable_autowire
from wired import ServiceRegistry
from zope.interface import Interface, implementer


class Iface00(Interface):
    pass


class Ctxt:
    pass


class IFoo(Interface):
    pass


@implementer(IFoo)
class Foo:
    @AutowireInit(
        impl00=Autowire(Iface00),
        impl01=Autowire(name="impl01"),
        impl02=Autowire(name=FromNamespace(name="n_impl02")),
        impl03=Autowire(context=FromNamespace(name="n_impl03")),
    )
    def __init__(self, impl00, impl01, impl02, impl03):
        self.impl00 = impl00
        self.impl01 = impl01
        self.impl02 = impl02
        self.impl03 = impl03


def test():
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
        Foo, IFoo, namespace=dict(n_impl02="r_impl02", n_impl03=Ctxt())
    )

    container = registry.create_container()
    foo = container.get(IFoo)
    assert foo.impl00 is impl00
    assert foo.impl01 is impl01
    assert foo.impl02 is impl02
    assert foo.impl03 is impl03
