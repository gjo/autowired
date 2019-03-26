from typing import Any, Dict, Optional, Text, Type
from pyramid.config import Configurator
from pyramid.request import Request
from zope.interface import Interface
from . import factory_factory


def register_autowire(
    config: Configurator,
    cls: Type,
    iface: Any = Interface,
    *,
    context: Optional[Interface] = None,
    name: Optional[Text] = "",
    namespace: Optional[Dict[Text, Any]] = None
) -> None:
    _factory = factory_factory(cls, namespace)

    def factory(context_: Any, request: Request) -> Any:
        container = request.services
        container = container.bind(context=context_)
        service = _factory(container)
        return service

    config.register_service_factory(factory, iface, context=context, name=name)


def includeme(config: Configurator) -> None:
    config.include("pyramid_services")
    config.add_directive("register_autowire", register_autowire)
