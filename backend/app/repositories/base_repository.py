from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, TypeVar, Generic

T = TypeVar('T')

class BaseRepository(ABC, Generic[T]):
    """
    Abstract base repository following Repository Pattern.
    Enforces LSP by being truly abstract - cannot be instantiated directly.
    Provides common functionality through template methods while requiring
    subclasses to implement domain-specific operations.
    """

    def __init__(self, db_executor):
        """
        Initialize repository with database executor.

        Args:
            db_executor: Database executor instance for query execution
        """
        self._db = db_executor

    @abstractmethod
    def _get_table_name(self) -> str:
        """Return the table name for this repository"""
        pass

    @abstractmethod
    def _get_id_column(self) -> str:
        """Return the primary key column name"""
        pass

    # Template Method Pattern - protected method for subclasses
    def _execute_query(
        self,
        query: str,
        params: tuple = None,
        fetch_one: bool = False
    ) -> Optional[Dict[str, Any]] | List[Dict[str, Any]]:
        """
        Protected template method for executing queries.
        Provides consistent error handling and result mapping.

        Args:
            query: SQL query string
            params: Query parameters tuple
            fetch_one: If True, return single dict; if False, return list of dicts

        Returns:
            Single dict if fetch_one=True, list of dicts otherwise, or None if no results
        """
        try:
            if fetch_one:
                result = self._db.fetch_one(query, params) if params else self._db.fetch_one(query, ())
                return dict(result) if result else None
            else:
                results = self._db.fetch_all(query, params) if params else self._db.fetch_all(query, ())
                return [dict(row) for row in results] if results else []
        except Exception as e:
            # Re-raise with context - let service layer handle domain exceptions
            raise Exception(f"Query execution failed: {str(e)}") from e

    # Common operations with default implementations
    def get_by_id(self, entity_id: int) -> Optional[Dict[str, Any]]:
        """
        Default implementation for getting entity by ID.
        Can be overridden by subclasses for custom behavior.

        Args:
            entity_id: Primary key value

        Returns:
            Entity as dict or None if not found
        """
        table = self._get_table_name()
        id_col = self._get_id_column()
        query = f'SELECT * FROM {table} WHERE {id_col} = %s'
        return self._execute_query(query, (entity_id,), fetch_one=True)

    def exists(self, entity_id: int) -> bool:
        """
        Check if entity exists.

        Args:
            entity_id: Primary key value

        Returns:
            True if entity exists, False otherwise
        """
        table = self._get_table_name()
        id_col = self._get_id_column()
        query = f'SELECT EXISTS(SELECT 1 FROM {table} WHERE {id_col} = %s) AS exists'
        result = self._execute_query(query, (entity_id,), fetch_one=True)
        return result['exists'] if result else False

    # Abstract methods that MUST be implemented by subclasses
    @abstractmethod
    def create(self, entity: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create new entity - must be implemented by subclass.
        Each subclass knows its specific fields and creation logic.

        Args:
            entity: Dictionary with entity data

        Returns:
            Created entity as dict or None if creation failed
        """
        pass

    @abstractmethod
    def update(self, entity_id: int, entity: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update entity - must be implemented by subclass.
        Each subclass knows its specific fields and update logic.

        Args:
            entity_id: Primary key value
            entity: Dictionary with updated entity data

        Returns:
            Updated entity as dict or None if update failed
        """
        pass

    @abstractmethod
    def delete(self, entity_id: int) -> bool:
        """
        Delete entity - must be implemented by subclass.
        Subclasses decide between hard delete or soft delete.

        Args:
            entity_id: Primary key value

        Returns:
            True if deletion successful, False otherwise
        """
        pass