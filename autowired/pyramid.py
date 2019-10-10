from typing import Any, Iterable, Mapping, Optional, Text, Type
from pyramid.config import Configurator
from pyramid.request import Request
from zope.interface import Interface
from . import factory_factory


def register_autowire(
    config: Configurator,
    cls: Type[Any],
    iface: Type[Interface] = Interface,
    *,
    context: Optional[Type[Interface]] = None,
    name: Optional[Text] = "",
    cls_args: Optional[Iterable[Any]] = None,
    cls_kwargs: Optional[Mapping[Text, Any]] = None,
    namespace: Optional[Mapping[Text, Any]] = None,
    lazy: bool = False
) -> None:
    _factory = factory_factory(cls, cls_args, cls_kwargs, namespace, lazy)

    def factory(context_: Any, request: Request) -> Any:
        container = request.services
        container = container.bind(context=context_)
        service = _factory(container)
        return service

    config.register_service_factory(factory, iface, context=context, name=name)


def includeme(config: Configurator) -> None:
    config.include("pyramid_services")
    config.add_directive("register_autowire", register_autowire)
