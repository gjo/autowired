from types import MethodType
from typing import (
    Any,
    Callable,
    Iterable,
    Mapping,
    Optional,
    Text,
    Type,
    TypeVar,
    Union,
)
from wired import ServiceContainer, ServiceRegistry
from zope.interface import Interface

__version__ = "0.1.dev0"


T = TypeVar("T")


class AutowireError(Exception):
    pass


class DoesNotWired(AutowireError, AttributeError):
    pass


class DoesNotSupportLazy(AutowireError, ValueError):
    pass


class DataSource:
    pass


class FromProperty(DataSource):
    __slots__ = ["name"]

    def __init__(self, name: Text) -> None:
        self.name = name


class FromNamespace(DataSource):
    __slots__ = ["name"]

    def __init__(self, name: Text) -> None:
        self.name = name


FROM_SELF = DataSource()


class Autowire:
    __slots__ = ["iface_or_type", "context", "name"]

    def __init__(
        self,
        iface_or_type: Type[Any] = Interface,
        *,
        context: Optional[DataSource] = None,
        name: Optional[Union[Text, DataSource]] = None
    ) -> None:
        self.iface_or_type = iface_or_type
        self.context = context
        self.name = name

    def raise_if_using_lazy(self) -> None:
        if (
            isinstance(self.context, FromProperty)
            or isinstance(self.name, FromProperty)
            or self.context is FROM_SELF
            or self.name is FROM_SELF
        ):
            raise DoesNotSupportLazy

    def resolved(
        self,
        container: ServiceContainer,
        obj: Any = None,
        namespace: Optional[Mapping[Text, Any]] = None,
    ) -> Any:
        params = {}
        if self.context:
            if self.context is FROM_SELF:
                assert obj
                params["context"] = obj
            elif isinstance(self.context, FromNamespace):
                assert namespace
                params["context"] = namespace[self.context.name]
            elif isinstance(self.context, FromProperty):
                assert obj
                params["context"] = getattr(obj, self.context.name)
        if self.name:
            if isinstance(self.name, FromNamespace):
                assert namespace
                params["name"] = namespace[self.name.name]
            elif isinstance(self.name, FromProperty):
                assert obj
                params["name"] = getattr(obj, self.name.name)
            else:
                params["name"] = self.name
        return container.get(self.iface_or_type, **params)


class AutowireField(Autowire):
    """
    A property descriptor for wired service.
    """

    __slots__ = Autowire.__slots__.copy()

    def __get__(self, obj: Any, type: Optional[type] = None) -> Any:
        if obj is None:
            return self

        if not hasattr(obj, "_autowire_field_lazy_loader"):
            raise DoesNotWired
        lazy_loader = (
            obj._autowire_field_lazy_loader
        )  # type: AutowireFieldLazyLoader
        property_name = lazy_loader.property_map[self]
        service = self.resolved(
            lazy_loader.container, obj, lazy_loader.namespace
        )
        setattr(obj, property_name, service)
        return service


class AutowireFieldLazyLoader:
    __slots__ = ["container", "namespace", "property_map"]

    def __init__(
        self,
        container: ServiceContainer,
        namespace: Mapping[Text, Any],
        property_map: Mapping[AutowireField, Text],
    ) -> None:
        self.container = container
        self.namespace = namespace
        self.property_map = property_map


class AutowireInit:
    __slots__ = ["kwargs"]

    def __init__(self, **kwargs: Autowire) -> None:
        self.kwargs = kwargs

    def __call__(self, func: T) -> T:
        setattr(func, "_autowire_init", self)
        return func

    def raise_if_using_lazy(self) -> None:
        for k, a in self.kwargs.items():
            a.raise_if_using_lazy()

    def resolved(
        self, container: ServiceContainer, namespace: Mapping[Text, Any]
    ) -> Mapping[Text, Any]:
        return {
            k: a.resolved(container, None, namespace)
            for k, a in self.kwargs.items()
        }


def factory_factory(
    cls: Type[Any],
    cls_args: Optional[Iterable[Any]] = None,
    cls_kwargs: Optional[Mapping[Text, Any]] = None,
    namespace: Optional[Mapping[Text, Any]] = None,
    lazy: bool = False,
) -> Callable[[ServiceContainer], Any]:
    _namespace = namespace if namespace else {}
    property_map = {
        v: k for k, v in cls.__dict__.items() if isinstance(v, AutowireField)
    }
    if not lazy:
        for af, _ in property_map.items():
            af.raise_if_using_lazy()

    ai = getattr(
        cls.__init__, "_autowire_init", None
    )  # type: Optional[AutowireInit]
    if ai:
        ai.raise_if_using_lazy()

    def factory(container: ServiceContainer) -> Any:
        _cls_kwargs = dict(cls_kwargs) if cls_kwargs else {}
        if ai:
            _cls_kwargs.update(ai.resolved(container, _namespace))
        if cls_args:
            if _cls_kwargs:
                svc = cls(*cls_args, **_cls_kwargs)
            else:
                svc = cls(*cls_args)
        else:
            if _cls_kwargs:
                svc = cls(**_cls_kwargs)
            else:
                svc = cls()
        if lazy:
            svc._autowire_field_lazy_loader = AutowireFieldLazyLoader(
                container, _namespace, property_map
            )
        else:
            for af, pn in property_map.items():
                setattr(svc, pn, af.resolved(container, svc, _namespace))
        return svc

    return factory


def register_autowire(
    registry: ServiceRegistry,
    cls: Type[Any],
    iface: Type[Any] = Interface,
    *,
    context: Optional[Type[Any]] = None,
    name: Text = "",
    cls_args: Optional[Iterable[Any]] = None,
    cls_kwargs: Optional[Mapping[Text, Any]] = None,
    namespace: Optional[Mapping[Text, Any]] = None,
    lazy: bool = False
) -> None:
    factory = factory_factory(cls, cls_args, cls_kwargs, namespace, lazy)
    registry.register_factory(factory, iface, context=context, name=name)


def enable_autowire(registry: ServiceRegistry) -> None:
    registry.register_autowire = MethodType(register_autowire, registry)
