import pytest
from autowired import (
    Autowire,
    AutowireField,
    AutowireInit,
    DoesNotWired,
    DoesNotSupportLazy,
    FROM_SELF,
    enable_autowire,
)
from wired import ServiceRegistry


def test_does_not_wired():
    class Foo:
        f1 = AutowireField()

    foo = Foo()
    pytest.raises(DoesNotWired, getattr, foo, "f1")


def test_does_not_support_lazy_eager():
    class Foo:
        f1 = AutowireField(context=FROM_SELF)

    registry = ServiceRegistry()
    enable_autowire(registry)
    pytest.raises(DoesNotSupportLazy, registry.register_autowire, Foo)


def test_does_not_support_lazy_init():
    class Foo:
        @AutowireInit(f1=Autowire(context=FROM_SELF))
        def __init__(self, **kwargs):  # pragma: no cover
            pass

    registry = ServiceRegistry()
    enable_autowire(registry)
    pytest.raises(DoesNotSupportLazy, registry.register_autowire, Foo)
