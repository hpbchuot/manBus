from app.core.interfaces.repository import IRepository
from abc import abstractmethod

class BaseRepository(IRepository):
    """Base implementation with common logic"""

    def __init__(self, db_executor):
        self._db = db_executor

    def _execute_query(self, query, params):
        # Protected method for subclasses
        return self._db.execute_query(query, params)

    @abstractmethod
    def _get_table_name(self):
        """Subclasses must provide table name"""
        pass

    @abstractmethod
    def _get_id_column(self):
        """Subclasses must provide ID column name"""
        pass

    def create(self, entity):
        """Create new entity - must be overridden by subclasses with specific fields"""
        raise NotImplementedError("Subclasses must implement create() with specific fields")

    def update(self, entity):
        """Update entity - must be overridden by subclasses with specific fields"""
        raise NotImplementedError("Subclasses must implement update() with specific fields")

    def delete(self, id):
        """Soft delete entity by ID"""
        query = f'UPDATE {self._get_table_name()} SET is_deleted = TRUE WHERE {self._get_id_column()} = %s'
        return self._execute_query(query, (id,))