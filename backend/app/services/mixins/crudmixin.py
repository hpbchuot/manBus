from typing import Optional, Dict, Any, Generic, TypeVar
from abc import ABC

T = TypeVar('T')

class CrudMixin(ABC, Generic[T]):
    """
    Mixin providing basic CRUD operations.
    Single Responsibility: Create, Read, Update, Delete
    """

    def __init__(self, repository):
        self.repository = repository

    def get_by_id(self, entity_id: int) -> Optional[T]:
        """Get single entity by ID"""
        entity_dict = self.repository.get_by_id(entity_id)
        return self._to_schema(entity_dict) if entity_dict else None

    def create(self, data: Dict[str, Any]) -> Optional[T]:
        """Create new entity"""
        entity_dict = self.repository.create(data)
        return self._to_schema(entity_dict) if entity_dict else None

    def update(self, entity_id: int, data: Dict[str, Any]) -> Optional[T]:
        """Update existing entity"""
        entity_dict = self.repository.update(entity_id, data)
        return self._to_schema(entity_dict) if entity_dict else None

    def delete(self, entity_id: int) -> bool:
        """Delete entity"""
        return self.repository.delete(entity_id)

    def exists(self, entity_id: int) -> bool:
        """Check if entity exists"""
        return self.repository.exists(entity_id)

    def _to_schema(self, entity_dict: Dict[str, Any]) -> T:
        """Convert dict to Pydantic schema - override in subclass"""
        raise NotImplementedError("Subclass must implement _to_schema")