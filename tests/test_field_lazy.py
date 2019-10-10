from autowired import (
    AutowireField,
    FROM_SELF,
    FromNamespace,
    FromProperty,
    enable_autowire,
)
from wired import ServiceRegistry
from zope.interface import Interface, implementer


class Iface00(Interface):
    pass


class Ctxt:
    pass


class Ctxt2:
    pass


class IFoo(Interface):
    pass


@implementer(IFoo)
class Foo:
    impl00 = AutowireField(Iface00)
    impl01 = AutowireField(name="impl01")
    impl02 = AutowireField(name=FromNamespace(name="n_impl02"))
    impl03 = AutowireField(context=FromNamespace(name="n_impl03"))
    impl04 = AutowireField(name=FromProperty(name="p_impl04"))
    impl05 = AutowireField(context=FromProperty(name="p_impl05"))
    impl06 = AutowireField(context=FROM_SELF)

    def __init__(self, p_impl04, p_impl05):
        self.p_impl04 = p_impl04
        self.p_impl05 = p_impl05


def assert_lazy(cls_args, cls_kwargs):
    assert isinstance(Foo.impl00, AutowireField)
    assert isinstance(Foo.impl01, AutowireField)
    assert isinstance(Foo.impl02, AutowireField)
    assert isinstance(Foo.impl03, AutowireField)
    assert isinstance(Foo.impl04, AutowireField)
    assert isinstance(Foo.impl05, AutowireField)
    assert isinstance(Foo.impl06, AutowireField)

    registry = ServiceRegistry()
    enable_autowire(registry)

    impl00 = object()
    impl01 = object()
    impl02 = object()
    impl03 = object()
    impl04 = object()
    impl05 = object()
    impl06 = object()

    registry.register_singleton(impl00, Iface00)
    registry.register_singleton(impl01, name="impl01")
    registry.register_singleton(impl02, name="r_impl02")
    registry.register_singleton(impl03, context=Ctxt)
    registry.register_singleton(impl04, name="pv_impl04")
    registry.register_singleton(impl05, context=Ctxt2)
    registry.register_singleton(impl06, context=IFoo)
    registry.register_autowire(
        Foo,
        IFoo,
        namespace=dict(n_impl02="r_impl02", n_impl03=Ctxt()),
        cls_args=cls_args,
        cls_kwargs=cls_kwargs,
        lazy=True,
    )

    container = registry.create_container()
    foo = container.get(IFoo)
    assert foo.impl00 is impl00
    assert foo.impl01 is impl01
    assert foo.impl02 is impl02
    assert foo.impl03 is impl03
    assert foo.impl04 is impl04
    assert foo.impl05 is impl05
    assert foo.impl06 is impl06


def test_args():
    assert_lazy(("pv_impl04", Ctxt2()), None)


def test_kwargs():
    assert_lazy(None, {"p_impl04": "pv_impl04", "p_impl05": Ctxt2()})


def test_args_kwargs():
    assert_lazy(("pv_impl04",), {"p_impl05": Ctxt2()})
