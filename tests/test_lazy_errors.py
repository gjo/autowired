import pytest
from autowired import (
    AutowireTo,
    DoesNotDefinedPropertyName,
    IsNotLazyAutowireService,
)


def test_does_not_defined_property_name():
    aw = AutowireTo()
    with pytest.raises(DoesNotDefinedPropertyName):
        aw.__get__(object())


def test_is_not_lazy_autowire_service():
    aw = AutowireTo()
    aw.property_name = "TEST"
    with pytest.raises(IsNotLazyAutowireService):
        aw.__get__(object())
