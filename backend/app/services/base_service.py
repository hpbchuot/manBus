"""
Base service class with common CRUD operations and utilities.
All service classes should inherit from this base.
"""
from typing import TypeVar, Generic, Optional, List, Dict, Any, Type
from abc import ABC, abstractmethod
import logging

from app.config.database import Database
from app.schemas.base_schema import PaginationParams, PaginatedResponse

logger = logging.getLogger(__name__)

T = TypeVar('T')


class BaseService(ABC, Generic[T]):
    """
    Base service class providing common CRUD operations.

    Attributes:
        db: Database instance for query execution
        table_name: Name of the database table
        id_field: Primary key field name (default: 'id')
    """

    def __init__(self, db: Database, table_name: str, id_field: str = 'id'):
        """
        Initialize base service.

        Args:
            db: Database instance
            table_name: Name of the table this service manages
            id_field: Primary key field name
        """
        self.db = db
        self.table_name = table_name
        self.id_field = id_field

    def get_by_id(self, entity_id: int) -> Optional[Dict[str, Any]]:
        """
        Get entity by ID.

        Args:
            entity_id: Entity ID

        Returns:
            Entity data as dict or None if not found
        """
        try:
            query = f"""
                SELECT * FROM {self.table_name}
                WHERE {self.id_field} = %s
            """
            result = self.db.fetch_one(query, (entity_id,))
            return dict(result) if result else None
        except Exception as e:
            logger.error(f"Error getting {self.table_name} by id {entity_id}: {e}")
            raise

    def get_all(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Get all entities with optional filters.

        Args:
            filters: Dictionary of field:value filters

        Returns:
            List of entity dicts
        """
        try:
            query = f"SELECT * FROM {self.table_name}"
            params = []

            if filters:
                where_clauses = []
                for field, value in filters.items():
                    where_clauses.append(f"{field} = %s")
                    params.append(value)
                query += " WHERE " + " AND ".join(where_clauses)

            results = self.db.fetch_all(query, tuple(params) if params else None)
            return [dict(row) for row in results] if results else []
        except Exception as e:
            logger.error(f"Error getting all {self.table_name}: {e}")
            raise

    def create(self, data: Dict[str, Any], returning_fields: str = '*') -> Optional[Dict[str, Any]]:
        """
        Create a new entity.

        Args:
            data: Dictionary of field:value pairs
            returning_fields: Fields to return (default: all)

        Returns:
            Created entity data
        """
        try:
            fields = ', '.join(data.keys())
            placeholders = ', '.join(['%s'] * len(data))
            values = tuple(data.values())

            query = f"""
                INSERT INTO {self.table_name} ({fields})
                VALUES ({placeholders})
                RETURNING {returning_fields}
            """

            result = self.db.fetch_one(query, values)
            return dict(result) if result else None
        except Exception as e:
            logger.error(f"Error creating {self.table_name}: {e}")
            raise

    def update(
        self,
        entity_id: int,
        data: Dict[str, Any],
        returning_fields: str = '*'
    ) -> Optional[Dict[str, Any]]:
        """
        Update an entity by ID.

        Args:
            entity_id: Entity ID
            data: Dictionary of field:value pairs to update
            returning_fields: Fields to return (default: all)

        Returns:
            Updated entity data or None if not found
        """
        try:
            if not data:
                raise ValueError("No data provided for update")

            set_clauses = []
            values = []
            for field, value in data.items():
                set_clauses.append(f"{field} = %s")
                values.append(value)

            values.append(entity_id)

            query = f"""
                UPDATE {self.table_name}
                SET {', '.join(set_clauses)}
                WHERE {self.id_field} = %s
                RETURNING {returning_fields}
            """

            result = self.db.fetch_one(query, tuple(values))
            return dict(result) if result else None
        except Exception as e:
            logger.error(f"Error updating {self.table_name} id {entity_id}: {e}")
            raise

    def delete(self, entity_id: int) -> bool:
        """
        Delete an entity by ID (hard delete).

        Args:
            entity_id: Entity ID

        Returns:
            True if deleted, False if not found
        """
        try:
            query = f"""
                DELETE FROM {self.table_name}
                WHERE {self.id_field} = %s
                RETURNING {self.id_field}
            """
            result = self.db.fetch_one(query, (entity_id,))
            return result is not None
        except Exception as e:
            logger.error(f"Error deleting {self.table_name} id {entity_id}: {e}")
            raise

    def soft_delete(self, entity_id: int) -> Optional[Dict[str, Any]]:
        """
        Soft delete an entity by setting is_deleted=True and deleted_at.

        Args:
            entity_id: Entity ID

        Returns:
            Updated entity data or None if not found
        """
        try:
            query = f"""
                UPDATE {self.table_name}
                SET is_deleted = TRUE, deleted_at = NOW()
                WHERE {self.id_field} = %s
                RETURNING *
            """
            result = self.db.fetch_one(query, (entity_id,))
            return dict(result) if result else None
        except Exception as e:
            logger.error(f"Error soft deleting {self.table_name} id {entity_id}: {e}")
            raise

    def restore(self, entity_id: int) -> Optional[Dict[str, Any]]:
        """
        Restore a soft-deleted entity.

        Args:
            entity_id: Entity ID

        Returns:
            Restored entity data or None if not found
        """
        try:
            query = f"""
                UPDATE {self.table_name}
                SET is_deleted = FALSE, deleted_at = NULL
                WHERE {self.id_field} = %s
                RETURNING *
            """
            result = self.db.fetch_one(query, (entity_id,))
            return dict(result) if result else None
        except Exception as e:
            logger.error(f"Error restoring {self.table_name} id {entity_id}: {e}")
            raise

    def exists(self, entity_id: int) -> bool:
        """
        Check if an entity exists.

        Args:
            entity_id: Entity ID

        Returns:
            True if exists, False otherwise
        """
        try:
            query = f"""
                SELECT 1 FROM {self.table_name}
                WHERE {self.id_field} = %s
            """
            result = self.db.fetch_one(query, (entity_id,))
            return result is not None
        except Exception as e:
            logger.error(f"Error checking existence of {self.table_name} id {entity_id}: {e}")
            raise

    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count entities with optional filters.

        Args:
            filters: Dictionary of field:value filters

        Returns:
            Count of entities
        """
        try:
            query = f"SELECT COUNT(*) as count FROM {self.table_name}"
            params = []

            if filters:
                where_clauses = []
                for field, value in filters.items():
                    where_clauses.append(f"{field} = %s")
                    params.append(value)
                query += " WHERE " + " AND ".join(where_clauses)

            result = self.db.fetch_one(query, tuple(params) if params else None)
            return result['count'] if result else 0
        except Exception as e:
            logger.error(f"Error counting {self.table_name}: {e}")
            raise

    def paginate(
        self,
        pagination: PaginationParams,
        filters: Optional[Dict[str, Any]] = None,
        order_by: str = None
    ) -> Dict[str, Any]:
        """
        Get paginated results.

        Args:
            pagination: Pagination parameters
            filters: Optional filters
            order_by: Optional ORDER BY clause (e.g., "created_at DESC")

        Returns:
            Dictionary with items, total, and pagination info
        """
        try:
            # Build base query
            base_query = f"FROM {self.table_name}"
            params = []

            if filters:
                where_clauses = []
                for field, value in filters.items():
                    where_clauses.append(f"{field} = %s")
                    params.append(value)
                base_query += " WHERE " + " AND ".join(where_clauses)

            # Get total count
            count_query = f"SELECT COUNT(*) as count {base_query}"
            count_result = self.db.fetch_one(count_query, tuple(params) if params else None)
            total = count_result['count'] if count_result else 0

            # Get paginated items
            select_query = f"SELECT * {base_query}"
            if order_by:
                select_query += f" ORDER BY {order_by}"
            select_query += f" LIMIT %s OFFSET %s"

            params.extend([pagination.limit, pagination.offset])
            results = self.db.fetch_all(select_query, tuple(params))
            items = [dict(row) for row in results] if results else []

            return {
                'items': items,
                'total': total,
                'page': pagination.page,
                'page_size': pagination.page_size,
                'total_pages': (total + pagination.page_size - 1) // pagination.page_size if total > 0 else 0,
                'has_next': pagination.page < ((total + pagination.page_size - 1) // pagination.page_size),
                'has_prev': pagination.page > 1
            }
        except Exception as e:
            logger.error(f"Error paginating {self.table_name}: {e}")
            raise

    def bulk_create(self, data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Create multiple entities in a single transaction.

        Args:
            data_list: List of dictionaries with entity data

        Returns:
            List of created entity dicts
        """
        if not data_list:
            return []

        try:
            # Assuming all dicts have the same keys
            fields = ', '.join(data_list[0].keys())
            placeholders = ', '.join(['%s'] * len(data_list[0]))

            # Build values for all rows
            all_values = []
            for data in data_list:
                all_values.extend(data.values())

            # Build query with multiple value sets
            value_sets = ', '.join([f"({placeholders})" for _ in data_list])

            query = f"""
                INSERT INTO {self.table_name} ({fields})
                VALUES {value_sets}
                RETURNING *
            """

            results = self.db.fetch_all(query, tuple(all_values))
            return [dict(row) for row in results] if results else []
        except Exception as e:
            logger.error(f"Error bulk creating {self.table_name}: {e}")
            raise

    def find_by(self, field: str, value: Any) -> Optional[Dict[str, Any]]:
        """
        Find a single entity by a specific field.

        Args:
            field: Field name to search
            value: Value to match

        Returns:
            Entity dict or None
        """
        try:
            query = f"""
                SELECT * FROM {self.table_name}
                WHERE {field} = %s
                LIMIT 1
            """
            result = self.db.fetch_one(query, (value,))
            return dict(result) if result else None
        except Exception as e:
            logger.error(f"Error finding {self.table_name} by {field}: {e}")
            raise

    def find_all_by(self, field: str, value: Any) -> List[Dict[str, Any]]:
        """
        Find all entities matching a specific field value.

        Args:
            field: Field name to search
            value: Value to match

        Returns:
            List of entity dicts
        """
        try:
            query = f"""
                SELECT * FROM {self.table_name}
                WHERE {field} = %s
            """
            results = self.db.fetch_all(query, (value,))
            return [dict(row) for row in results] if results else []
        except Exception as e:
            logger.error(f"Error finding all {self.table_name} by {field}: {e}")
            raise
