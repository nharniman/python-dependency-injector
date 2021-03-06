from __future__ import annotations

from pathlib import Path
from typing import (
    TypeVar,
    Generic,
    Type,
    Callable as _Callable,
    Any,
    Tuple,
    List as _List,
    Dict as _Dict,
    Optional,
    Union,
    Coroutine as _Coroutine,
    Iterator as _Iterator,
    Generator as _Generator,
    overload,
)

from . import resources


Injection = Any
T = TypeVar('T')


class OverridingContext:
    def __init__(self, overridden: Provider, overriding: Provider): ...
    def __enter__(self) -> Provider: ...
    def __exit__(self, *_: Any) -> None: ...


class Provider(Generic[T]):
    def __init__(self) -> None: ...
    def __call__(self, *args: Injection, **kwargs: Injection) -> T: ...
    def __deepcopy__(self, memo: Optional[_Dict[Any, Any]]) -> Provider: ...
    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...
    @property
    def overridden(self) -> Tuple[Provider]: ...
    @property
    def last_overriding(self) -> Optional[Provider]: ...
    def override(self, provider: Union[Provider, Any]) -> OverridingContext: ...
    def reset_last_overriding(self) -> None: ...
    def reset_override(self) -> None: ...
    def delegate(self) -> Provider: ...
    @property
    def provider(self) -> Provider: ...
    @property
    def provided(self) -> ProvidedInstance: ...
    def _copy_overridings(self, copied: Provider, memo: Optional[_Dict[Any, Any]]) -> None: ...


class Object(Provider, Generic[T]):
    def __init__(self, provides: T) -> None: ...
    def __call__(self, *args: Injection, **kwargs: Injection) -> T: ...


class Delegate(Provider):
    def __init__(self, provides: Provider) -> None: ...
    def __call__(self, *args: Injection, **kwargs: Injection) -> Provider: ...
    @property
    def provides(self) -> Provider: ...


class Dependency(Provider, Generic[T]):
    def __init__(self, instance_of: Type[T] = object) -> None: ...
    def __call__(self, *args: Injection, **kwargs: Injection) -> T: ...
    @property
    def instance_of(self) -> Type[T]: ...
    def provided_by(self, provider: Provider) -> OverridingContext: ...


class ExternalDependency(Dependency): ...


class DependenciesContainer(Object):
    def __init__(self, **dependencies: Provider) -> None: ...
    def __getattr__(self, name: str) -> Provider: ...
    @property
    def providers(self) -> _Dict[str, Provider]: ...


class Callable(Provider, Generic[T]):
    def __init__(self, provides: _Callable[..., T], *args: Injection, **kwargs: Injection) -> None: ...
    def __call__(self, *args: Injection, **kwargs: Injection) -> T: ...
    @property
    def provides(self) -> T: ...
    @property
    def args(self) -> Tuple[Injection]: ...
    def add_args(self, *args: Injection) -> Callable[T]: ...
    def set_args(self, *args: Injection) -> Callable[T]: ...
    def clear_args(self) -> Callable[T]: ...
    @property
    def kwargs(self) -> _Dict[str, Injection]: ...
    def add_kwargs(self, **kwargs: Injection) -> Callable[T]: ...
    def set_kwargs(self, **kwargs: Injection) -> Callable[T]: ...
    def clear_kwargs(self) -> Callable[T]: ...


class DelegatedCallable(Callable): ...


class AbstractCallable(Callable):
    def override(self, provider: Callable) -> OverridingContext: ...


class CallableDelegate(Delegate):
    def __init__(self, callable: Callable) -> None: ...


class Coroutine(Callable): ...


class DelegatedCoroutine(Coroutine): ...


class AbstractCoroutine(Coroutine):
    def override(self, provider: Coroutine) -> OverridingContext: ...


class CoroutineDelegate(Delegate):
    def __init__(self, coroutine: Coroutine) -> None: ...


class ConfigurationOption(Provider):
    UNDEFINED: object
    def __init__(self, name: Tuple[str], root: Configuration) -> None: ...
    def __call__(self, *args: Injection, **kwargs: Injection) -> Any: ...
    def __getattr__(self, item: str) -> ConfigurationOption: ...
    def __getitem__(self, item: Union[str, Provider]) -> ConfigurationOption: ...
    @property
    def root(self) -> Configuration: ...
    def get_name(self) -> str: ...
    def get_name_segments(self) -> Tuple[Union[str, Provider]]: ...
    def as_int(self) -> TypedConfigurationOption[int]: ...
    def as_float(self) -> TypedConfigurationOption[float]: ...
    def as_(self, callback: _Callable[..., T], *args: Injection, **kwargs: Injection) -> TypedConfigurationOption[T]: ...
    def update(self, value: Any) -> None: ...
    def from_ini(self, filepath: Union[Path, str]) -> None: ...
    def from_yaml(self, filepath: Union[Path, str]) -> None: ...
    def from_dict(self, options: _Dict[str, Any]) -> None: ...
    def from_env(self, name: str, default: Optional[Any] = None) -> None: ...


class TypedConfigurationOption(Callable[T]):
    @property
    def option(self) -> ConfigurationOption: ...


class Configuration(Object):
    DEFAULT_NAME: str = 'config'
    def __init__(self, name: str = DEFAULT_NAME, default: Optional[Any] = None) -> None: ...
    def __getattr__(self, item: str) -> ConfigurationOption: ...
    def __getitem__(self, item: Union[str, Provider]) -> ConfigurationOption: ...
    def get_name(self) -> str: ...
    def get(self, selector: str) -> Any: ...
    def set(self, selector: str, value: Any) -> OverridingContext: ...
    def reset_cache(self) -> None: ...
    def update(self, value: Any) -> None: ...
    def from_ini(self, filepath: Union[Path, str]) -> None: ...
    def from_yaml(self, filepath: Union[Path, str]) -> None: ...
    def from_dict(self, options: _Dict[str, Any]) -> None: ...
    def from_env(self, name: str, default: Optional[Any] = None) -> None: ...


class Factory(Provider, Generic[T]):
    provided_type: Optional[Type]
    def __init__(self, provides: _Callable[..., T], *args: Injection, **kwargs: Injection) -> None: ...
    def __call__(self, *args: Injection, **kwargs: Injection) -> T: ...
    @property
    def cls(self) -> T: ...
    @property
    def provides(self) -> T: ...
    @property
    def args(self) -> Tuple[Injection]: ...
    def add_args(self, *args: Injection) -> Factory[T]: ...
    def set_args(self, *args: Injection) -> Factory[T]: ...
    def clear_args(self) -> Factory[T]: ...
    @property
    def kwargs(self) -> _Dict[str, Injection]: ...
    def add_kwargs(self, **kwargs: Injection) -> Factory[T]: ...
    def set_kwargs(self, **kwargs: Injection) -> Factory[T]: ...
    def clear_kwargs(self) -> Factory[T]: ...
    @property
    def attributes(self) -> _Dict[str, Injection]: ...
    def add_attributes(self, **kwargs: Injection) -> Factory[T]: ...
    def set_attributes(self, **kwargs: Injection) -> Factory[T]: ...
    def clear_attributes(self) -> Factory[T]: ...


class DelegatedFactory(Factory): ...


class AbstractFactory(Factory):
    def override(self, provider: Factory) -> OverridingContext: ...


class FactoryDelegate(Delegate):
    def __init__(self, factory: Factory): ...


class FactoryAggregate(Provider):
    def __init__(self, **factories: Factory): ...
    def __call__(self, factory_name: str, *args: Injection, **kwargs: Injection) -> Any: ...
    def __getattr__(self, factory_name: str) -> Factory: ...
    @property
    def factories(self) -> _Dict[str, Factory]: ...


class BaseSingleton(Provider, Generic[T]):
    provided_type = Optional[Type]
    def __init__(self, provides: _Callable[..., T], *args: Injection, **kwargs: Injection) -> None: ...
    def __call__(self, *args: Injection, **kwargs: Injection) -> T: ...
    @property
    def cls(self) -> T: ...
    @property
    def args(self) -> Tuple[Injection]: ...
    def add_args(self, *args: Injection) -> Factory[T]: ...
    def set_args(self, *args: Injection) -> Factory[T]: ...
    def clear_args(self) -> Factory[T]: ...
    @property
    def kwargs(self) -> _Dict[str, Injection]: ...
    def add_kwargs(self, **kwargs: Injection) -> Factory[T]: ...
    def set_kwargs(self, **kwargs: Injection) -> Factory[T]: ...
    def clear_kwargs(self) -> Factory[T]: ...
    @property
    def attributes(self) -> _Dict[str, Injection]: ...
    def add_attributes(self, **kwargs: Injection) -> Factory[T]: ...
    def set_attributes(self, **kwargs: Injection) -> Factory[T]: ...
    def clear_attributes(self) -> Factory[T]: ...
    def reset(self) -> None: ...


class Singleton(BaseSingleton): ...


class DelegatedSingleton(Singleton): ...


class ThreadSafeSingleton(Singleton): ...


class DelegatedThreadSafeSingleton(ThreadSafeSingleton): ...


class ThreadLocalSingleton(BaseSingleton): ...


class DelegatedThreadLocalSingleton(ThreadLocalSingleton): ...


class AbstractSingleton(BaseSingleton):
    def override(self, provider: BaseSingleton) -> OverridingContext: ...


class SingletonDelegate(Delegate):
    def __init__(self, factory: BaseSingleton): ...


class List(Provider):
    def __init__(self, *args: Injection): ...
    def __call__(self, *args: Injection, **kwargs: Injection) -> _List[Any]: ...
    @property
    def args(self) -> Tuple[Injection]: ...
    def add_args(self, *args: Injection) -> List: ...
    def set_args(self, *args: Injection) -> List: ...
    def clear_args(self) -> List: ...


class Dict(Provider):
    def __init__(self, dict_: Optional[_Dict[Any, Injection]] = None, **kwargs: Injection): ...
    def __call__(self, *args: Injection, **kwargs: Injection) -> _Dict[Any, Any]: ...
    @property
    def kwargs(self) -> _Dict[Any, Injection]: ...
    def add_kwargs(self, dict_: Optional[_Dict[Any, Injection]] = None, **kwargs: Injection) -> Dict: ...
    def set_kwargs(self, dict_: Optional[_Dict[Any, Injection]] = None, **kwargs: Injection) -> Dict: ...
    def clear_kwargs(self) -> Dict: ...


class Resource(Provider, Generic[T]):
    @overload
    def __init__(self, initializer: _Callable[..., resources.Resource[T]], *args: Injection, **kwargs: Injection) -> None: ...
    @overload
    def __init__(self, initializer: _Callable[..., _Iterator[T]], *args: Injection, **kwargs: Injection) -> None: ...
    @overload
    def __init__(self, initializer: _Callable[..., T], *args: Injection, **kwargs: Injection) -> None: ...
    def __call__(self, *args: Injection, **kwargs: Injection) -> T: ...
    @property
    def args(self) -> Tuple[Injection]: ...
    def add_args(self, *args: Injection) -> Resource: ...
    def set_args(self, *args: Injection) -> Resource: ...
    def clear_args(self) -> Resource: ...
    @property
    def kwargs(self) -> _Dict[Any, Injection]: ...
    def add_kwargs(self, **kwargs: Injection) -> Resource: ...
    def set_kwargs(self, **kwargs: Injection) -> Resource: ...
    def clear_kwargs(self) -> Resource: ...
    @property
    def initialized(self) -> bool: ...
    def init(self) -> T: ...
    def shutdown(self) -> None: ...


class Container(Provider):

    def __init__(self, container_cls: Type[T], container: Optional[T] = None, **overriding_providers: Provider) -> None: ...
    def __call__(self, *args: Injection, **kwargs: Injection) -> T: ...
    def __getattr__(self, name: str) -> Provider: ...
    @property
    def container(self) -> T: ...


class Selector(Provider):
    def __init__(self, selector: _Callable[..., Any], **providers: Provider): ...
    def __call__(self, *args: Injection, **kwargs: Injection) -> Any: ...
    def __getattr__(self, name: str) -> Provider: ...
    @property
    def providers(self) -> _Dict[str, Provider]: ...


class ProvidedInstanceFluentInterface:
    def __getattr__(self, item: Any) -> AttributeGetter: ...
    def __getitem__(self, item: Any) -> ItemGetter: ...
    def call(self, *args: Injection, **kwargs: Injection) -> MethodCaller: ...


class ProvidedInstance(Provider, ProvidedInstanceFluentInterface):
    def __init__(self, provider: Provider) -> None: ...


class AttributeGetter(Provider, ProvidedInstanceFluentInterface):
    def __init__(self, provider: Provider, attribute: str) -> None: ...


class ItemGetter(Provider, ProvidedInstanceFluentInterface):
    def __init__(self, provider: Provider, item: str) -> None: ...


class MethodCaller(Provider, ProvidedInstanceFluentInterface):
    def __init__(self, provider: Provider, *args: Injection, **kwargs: Injection) -> None: ...


def is_provider(instance: Any) -> bool: ...


def ensure_is_provider(instance: Any) -> Provider: ...


def is_delegated(instance: Any) -> bool: ...


def represent_provider(provider: Provider, provides: Any) -> str: ...


def deepcopy(instance: Any, memo: Optional[_Dict[Any, Any]] = None): Any: ...


def merge_dicts(dict1: _Dict[Any, Any], dict2: _Dict[Any, Any]) -> _Dict[Any, Any]: ...
