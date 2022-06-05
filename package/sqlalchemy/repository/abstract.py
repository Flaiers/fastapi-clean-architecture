from typing import (
    Any,
    Dict,
    Generic,
    Sequence,
    Type,
    TypeVar,
    overload,
)

from sqlalchemy.ext.declarative import (
    DeclarativeMeta,
    declarative_base,
)

Base: DeclarativeMeta = declarative_base()
Model = TypeVar('Model', bound=Base)


class AbstractRepository(Generic[Model]):

    model: Type[Model]

    @overload
    def create(self, **attrs) -> Model: ...

    @overload
    def create(self, attrs: Dict[str, Any]) -> Model: ...

    @overload
    def merge(self, instance: Model, **attrs) -> Model: ...

    @overload
    def merge(self, instance: Model, attrs: Dict[str, Any]) -> Model: ...

    @overload
    def has_pk(self, instance: Model) -> bool: ...

    @overload
    def get_pk(self, instance: Model) -> Dict[str, Any] | Any: ...

    @overload
    async def count(self, *where, **attrs) -> int: ...

    @overload
    async def delete(self, *where, **attrs) -> None: ...

    @overload
    async def find(self, *where, **attrs) -> Sequence[Model]: ...

    @overload
    async def find_one(self, *where, **attrs) -> Model | None: ...

    @overload
    async def find_one_or_fail(self, *where, **attrs) -> Model: ...

    @overload
    async def remove(self, instance: Model) -> None: ...

    @overload
    async def remove(self, instances: Sequence[Model]) -> None: ...

    @overload
    async def pre_save(self, instance: Model) -> Model: ...

    @overload
    async def pre_save(self, instances: Sequence[Model]) -> Sequence[Model]: ...

    @overload
    async def save(self, instance: Model) -> Model: ...

    @overload
    async def save(self, instances: Sequence[Model]) -> Sequence[Model]: ...
