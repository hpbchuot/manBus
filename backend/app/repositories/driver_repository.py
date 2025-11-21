from typing import Optional, List, Dict, Any
from .base_repository import BaseRepository


class DriverRepository(BaseRepository):
    """
    Repository for Driver entity.
    Encapsulates all data access logic for drivers using PostgreSQL functions.
    Follows Repository Pattern and DIP (Dependency Inversion Principle).
    """

    def _get_table_name(self) -> str:
        """Return the drivers table name"""
        return 'Drivers'

    def _get_id_column(self) -> str:
        """Return the primary key column name"""
        return 'id'

    # Create
    def create(self, entity: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a new driver using PostgreSQL function.

        Args:
            entity: Dict with keys: user_id, license_number, bus_id

        Returns:
            Created driver as dict or None
        """
        query = 'SELECT fn_create_driver(%s, %s, %s) AS result'
        params = (
            entity.get('user_id'),
            entity.get('license_number'),
            entity.get('bus_id')
        )
        result = self._execute_query(query, params, fetch_one=True)

        if result and result.get('result'):
            return self.get_by_id(result['result'])
        return None

    # Read operations
    def get_by_id(self, driver_id: int) -> Optional[Dict[str, Any]]:
        """
        Get driver by ID.

        Args:
            driver_id: Driver ID

        Returns:
            Driver dict or None if not found
        """
        query = 'SELECT * FROM Drivers WHERE id = %s'
        return self._execute_query(query, (driver_id,), fetch_one=True)

    def get_by_user_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get driver by user ID using PostgreSQL function.

        Args:
            user_id: User ID

        Returns:
            Driver dict with bus and route information or None if not found
        """
        query = 'SELECT * FROM fn_get_driver_by_user(%s)'
        return self._execute_query(query, (user_id,), fetch_one=True)

    def get_by_bus_id(self, bus_id: int) -> Optional[Dict[str, Any]]:
        """
        Get driver assigned to a specific bus using PostgreSQL function.

        Args:
            bus_id: Bus ID

        Returns:
            Driver dict or None if not found
        """
        query = 'SELECT * FROM fn_get_driver_by_bus(%s)'
        return self._execute_query(query, (bus_id,), fetch_one=True)

    def get_all_active(self) -> List[Dict[str, Any]]:
        """
        Get all active drivers using PostgreSQL function.

        Returns:
            List of active driver dicts with user, bus, and route information
        """
        query = 'SELECT * FROM fn_get_active_drivers()'
        return self._execute_query(query, (), fetch_one=False)

    def get_all(self, include_deleted_users: bool = False) -> List[Dict[str, Any]]:
        """
        Get all drivers using PostgreSQL function.

        Args:
            include_deleted_users: If True, include drivers whose users are deleted

        Returns:
            List of driver dicts
        """
        query = 'SELECT * FROM fn_get_all_drivers(%s)'
        return self._execute_query(query, (include_deleted_users,), fetch_one=False)

    def get_drivers_on_route(self, route_id: int) -> List[Dict[str, Any]]:
        """
        Get all drivers assigned to buses on a specific route using PostgreSQL function.

        Args:
            route_id: Route ID

        Returns:
            List of driver dicts with bus and route information
        """
        query = 'SELECT * FROM fn_get_drivers_on_route(%s)'
        return self._execute_query(query, (route_id,), fetch_one=False)

    def is_user_driver(self, user_id: int) -> bool:
        """
        Check if a user is a driver using PostgreSQL function.

        Args:
            user_id: User ID to check

        Returns:
            True if user is a driver, False otherwise
        """
        query = 'SELECT fn_is_user_driver(%s) AS result'
        result = self._execute_query(query, (user_id,), fetch_one=True)
        return result.get('result', False) if result else False

    # Update operations
    def update(self, driver_id: int, entity: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update driver information.

        Args:
            driver_id: Driver ID
            entity: Dict with updated driver data

        Returns:
            Updated driver dict or None
        """
        update_fields = []
        params = []

        if 'license_number' in entity:
            update_fields.append('license_number = %s')
            params.append(entity['license_number'])
        if 'bus_id' in entity:
            update_fields.append('bus_id = %s')
            params.append(entity['bus_id'])
        if 'status' in entity:
            update_fields.append('status = %s')
            params.append(entity['status'])

        if not update_fields:
            return self.get_by_id(driver_id)

        params.append(driver_id)
        query = f"UPDATE Drivers SET {', '.join(update_fields)} WHERE id = %s"

        self._db.execute(query, tuple(params))
        return self.get_by_id(driver_id)

    def update_status(self, driver_id: int, status: str) -> bool:
        """
        Update driver status using PostgreSQL function.

        Args:
            driver_id: Driver ID
            status: New status value (Active, Inactive, Suspended)

        Returns:
            True if update successful, False otherwise
        """
        query = 'SELECT fn_set_driver_status(%s, %s) AS result'
        result = self._execute_query(query, (driver_id, status), fetch_one=True)
        return result.get('result', False) if result else True  # Function returns BOOLEAN

    def update_license(self, driver_id: int, new_license: str) -> bool:
        """
        Update driver's license number using PostgreSQL function.

        Args:
            driver_id: Driver ID
            new_license: New license number

        Returns:
            True if update successful, False otherwise
        """
        query = 'SELECT fn_update_driver_license(%s, %s) AS result'
        result = self._execute_query(query, (driver_id, new_license), fetch_one=True)
        return result.get('result', False) if result else True  # Function returns BOOLEAN

    def assign_to_bus(self, driver_id: int, bus_id: int) -> bool:
        """
        Assign driver to a bus using PostgreSQL function.

        Args:
            driver_id: Driver ID
            bus_id: Bus ID

        Returns:
            True if assignment successful, False otherwise
        """
        query = 'SELECT fn_assign_bus_to_driver(%s, %s) AS result'
        result = self._execute_query(query, (driver_id, bus_id), fetch_one=True)
        return result.get('result', False) if result else True  # Function returns BOOLEAN

    # Delete
    def delete(self, driver_id: int) -> bool:
        """
        Hard delete a driver (use with caution).

        Args:
            driver_id: Driver ID

        Returns:
            True if deletion successful, False otherwise
        """
        query = 'DELETE FROM Drivers WHERE id = %s'
        try:
            self._db.execute(query, (driver_id,))
            return True
        except Exception:
            return False

    # Business queries
    def get_driver_count(self, status: Optional[str] = None) -> int:
        """
        Get count of drivers by status using PostgreSQL function.

        Args:
            status: Optional status filter (NULL for all)

        Returns:
            Number of drivers
        """
        query = 'SELECT fn_get_driver_count(%s) AS count'
        result = self._execute_query(query, (status,), fetch_one=True)
        return result.get('count', 0) if result else 0
