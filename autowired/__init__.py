from types import MethodType
from typing import Any, Callable, Dict, Optional, Text, Type, Union
from wired import ServiceContainer, ServiceRegistry
from zope.interface import Interface

__version__ = "0.1.dev0"


class AutowireError(Exception):
    pass


class DoesNotDefinedPropertyName(AttributeError, AutowireError):
    pass


class IsNotLazyAutowireService(AttributeError, AutowireError):
    pass


class FromProperty:
    """
    A marker for `context` and `name` that is `Autowired`'s arguments.
    """

    __slots__ = ["name"]

    def __init__(self, name: Text):
        self.name = name


class AutowireTo:
    """
    A property descriptor for wired service.

    TODO: py36
    :type interface: Type[Interface]
    :type context: Optional[FromProperty]
    :type name: Optional[Union[Text, FromProperty]]
    :type property_name: Optional[Text]
    """

    def __init__(
        self,
        iface: Type[Interface] = Interface,
        *,
        context: Optional[FromProperty] = None,
        name: Optional[Union[Text, FromProperty]] = None
    ) -> None:
        self.interface = iface
        self.context = context
        self.name = name
        self.property_name = None

    def __get__(self, obj, obj_type=None):
        if obj is None:
            return self

        if not self.property_name:
            raise DoesNotDefinedPropertyName
        # NOTE: isinstance(obj, LazyWiredService)
        if not hasattr(obj, "wired_container"):
            raise IsNotLazyAutowireService

        service = self.find_service(obj.wired_container, obj.__dict__)
        setattr(obj, self.property_name, service)
        return service

    def find_service(
        self, container: ServiceContainer, namespace: Dict[Text, Any]
    ) -> Any:
        kwargs = {}  # type: Dict[Text, Any]
        if self.context:
            kwargs["context"] = namespace[self.context.name]
        if self.name:
            if isinstance(self.name, FromProperty):
                kwargs["name"] = namespace[self.name.name]
            else:
                kwargs["name"] = self.name
        service = container.get(self.interface, **kwargs)
        return service


class LazyAutowireServiceMeta(type):
    def __init__(cls, name, bases, namespace):
        for k, v in namespace.items():
            if isinstance(v, AutowireTo):
                v.property_name = k
        cls.wired_container = None


class LazyAutowireService(metaclass=LazyAutowireServiceMeta):
    """
    A service class that contains `Autowired` property that is lazy loaded.

    TODO: py36
    :type wired_container: Optional[ServiceRegistry]
    """

    def __init__(
        self,
        *,
        wired_container: Optional[ServiceRegistry] = None,
        **kwargs: Any
    ) -> None:
        self.wired_container = wired_container
        for k, v in kwargs.items():
            setattr(self, k, v)


def factory_factory(
    cls: Type, namespace: Optional[Dict[Text, Any]] = None
) -> Callable[[ServiceContainer], Any]:
    # NOTE: issubclass(cls, LazyAutowireService)
    is_lazy_cls = hasattr(cls, "wired_container")
    if is_lazy_cls:
        preloads = {}  # type: Dict[Text, Any]
    else:
        preloads = {
            k: v for k, v in cls.__dict__.items() if isinstance(v, AutowireTo)
        }

    def factory(container: ServiceContainer) -> Any:
        kwargs = namespace.copy() if namespace else {}
        if is_lazy_cls:
            kwargs["wired_container"] = container
        else:
            for k, v in preloads.items():
                kwargs[k] = v.find_service(container, namespace=kwargs)
        svc = cls(**kwargs)
        return svc

    return factory


def register_autowire(
    registry: ServiceRegistry,
    cls: Type,
    iface: Any = Interface,
    *,
    context: Optional[Interface] = None,
    name: Optional[Text] = "",
    namespace: Optional[Dict[Text, Any]] = None
) -> None:
    factory = factory_factory(cls, namespace)
    registry.register_factory(factory, iface, context=context, name=name)


def enable_autowire(registry: ServiceRegistry) -> None:
    registry.register_autowire = MethodType(register_autowire, registry)
