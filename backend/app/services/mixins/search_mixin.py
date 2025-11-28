from typing import List, Dict, Any, Optional, Generic, TypeVar

T = TypeVar('T')

class SearchMixin(Generic[T]):
    """
    Mixin providing search and filtering operations.
    Single Responsibility: Search and Filter
    """

    def get_all(self, filters: Optional[Dict[str, Any]] = None) -> List[T]:
        """Get all entities with optional filters"""
        entities = self.repository.get_all(filters or {})
        return [self._to_schema(e) for e in entities]

    def find_by(self, field: str, value: Any) -> Optional[T]:
        """Find single entity by field value"""
        entity_dict = self.repository.find_by(field, value)
        return self._to_schema(entity_dict) if entity_dict else None

    def find_all_by(self, field: str, value: Any) -> List[T]:
        """Find all entities by field value"""
        entities = self.repository.find_all_by(field, value)
        return [self._to_schema(e) for e in entities]

    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count entities with optional filters"""
        return self.repository.count(filters or {})

    def search(self, search_term: str) -> List[T]:
        """Search entities by term"""
        entities = self.repository.search(search_term)
        return [self._to_schema(e) for e in entities]