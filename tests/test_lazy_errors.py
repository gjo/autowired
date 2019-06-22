import pytest
from autowired import (
    AutowireTo,
    DoesNotDefinedPropertyName,
    DoesNotSupportLazyAutowire,
)


def test_does_not_defined_property_name():
    aw = AutowireTo()
    with pytest.raises(DoesNotDefinedPropertyName):
        aw.__get__(object())


def test_does_not_support_lazy_autowire():
    aw = AutowireTo()
    aw.property_name = "TEST"
    with pytest.raises(DoesNotSupportLazyAutowire):
        aw.__get__(object())
