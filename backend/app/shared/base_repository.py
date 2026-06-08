"""Abstract repository template for concrete persistence implementations."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class AbstractRepository(ABC, Generic[T]):
    """Base template for all repository implementations.

    Concrete repositories extend this and implement get_by_id and save.
    Additional query methods are added per repository as needed.
    """

    @abstractmethod
    async def get_by_id(self, entity_id: str) -> T | None:
        """Return the entity with the given identifier or None."""

    @abstractmethod
    async def save(self, entity: T) -> T:
        """Persist the entity and return the saved instance."""
