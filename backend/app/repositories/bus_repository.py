from typing import Optional, List, Dict, Any
from .base_repository import BaseRepository


class BusRepository(BaseRepository):
    """
    Repository for Bus entity.
    Encapsulates all data access logic for buses using PostgreSQL functions.
    Follows Repository Pattern and DIP (Dependency Inversion Principle).
    """

    def _get_table_name(self) -> str:
        """Return the buses table name"""
        return 'Buses'

    def _get_id_column(self) -> str:
        """Return the primary key column name"""
        return 'bus_id'

    # Create
    def create(self, entity: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a new bus using PostgreSQL function.

        Args:
            entity: Dict with keys: plate_number, name, route_id, model, status

        Returns:
            Created bus as dict or None
        """
        query = 'SELECT fn_create_bus(%s, %s, %s, %s, %s) AS result'
        params = (
            entity.get('plate_number'),
            entity.get('name'),
            entity.get('route_id'),
            entity.get('model'),
            entity.get('status', 'Active')
        )
        result = self._execute_query(query, params, fetch_one=True)

        if result and result.get('result'):
            return self.get_by_id(result['result'])
        return None

    # Read operations
    def get_by_id(self, bus_id: int) -> Optional[Dict[str, Any]]:
        """
        Get bus by ID with related route information.

        Args:
            bus_id: Bus ID

        Returns:
            Bus dict or None if not found
        """

        query = 'SELECT * FROM fn_get_bus_by_id(%s)'
        return self._execute_query(query, (bus_id,), fetch_one=True)

    def get_by_plate_number(self, plate_number: str) -> Optional[Dict[str, Any]]:
        """
        Get bus by plate number using PostgreSQL function.

        Args:
            plate_number: Vehicle plate number

        Returns:
            Bus dict or None if not found
        """
        query = 'SELECT * FROM fn_get_bus_by_plate(%s)'
        return self._execute_query(query, (plate_number,), fetch_one=True)

    def get_all(
            self, 
            cursor: Optional[int] = None,
            limit: Optional[int] = 10,
            include_inactive: bool = False) -> List[Dict[str, Any]]:
        """
        Get all buses using PostgreSQL function.

        Args:
            include_inactive: If True, include inactive/maintenance/retired buses

        Returns:
            List of bus dicts
        """
        query = 'SELECT * FROM fn_get_all_buses(%s, %s, %s)'
        return self._execute_query(query, (cursor, limit, include_inactive), fetch_one=False)

    def get_by_route(self, route_id: int) -> List[Dict[str, Any]]:
        """
        Get all buses assigned to a specific route using PostgreSQL function.

        Args:
            route_id: Route ID

        Returns:
            List of bus dicts
        """
        query = 'SELECT * FROM fn_get_buses_on_route(%s)'
        return self._execute_query(query, (route_id,), fetch_one=False)

    def get_active_buses(self, cursor: Optional[int] = None, limit: Optional[int] = 10) -> List[Dict[str, Any]]:
        """
        Get all active buses.

        Returns:
            List of active bus dicts
        """
        return self.get_all(cursor, limit, include_inactive=False)

    def find_nearest_bus(
        self,
        latitude: float,
        longitude: float,
        route_id: Optional[int] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find nearest buses to a location using PostgreSQL function.

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            route_id: Optional route ID filter
            limit: Maximum number of results

        Returns:
            List of nearest bus dicts with distance
        """
        query = 'SELECT * FROM fn_find_nearest_bus(%s, %s, %s, %s)'
        return self._execute_query(query, (latitude, longitude, route_id, limit), fetch_one=False)

    # Update operations
    def update(self, bus_id: int, entity: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update bus information.

        Args:
            bus_id: Bus ID
            entity: Dict with updated bus data

        Returns:
            Updated bus dict or None
        """
        # Direct update query since there's no specific update function in SQL
        update_fields = []
        params = []

        if 'plate_number' in entity:
            update_fields.append('plate_number = %s')
            params.append(entity['plate_number'])
        if 'name' in entity:
            update_fields.append('name = %s')
            params.append(entity['name'])
        if 'model' in entity:
            update_fields.append('model = %s')
            params.append(entity['model'])
        if 'route_id' in entity:
            update_fields.append('route_id = %s')
            params.append(entity['route_id'])
        if 'status' in entity:
            update_fields.append('status = %s')
            params.append(entity['status'])

        if not update_fields:
            return self.get_by_id(bus_id)

        params.append(bus_id)
        query = f"UPDATE Buses SET {', '.join(update_fields)} WHERE bus_id = %s"

        self._db.execute(query, tuple(params))
        return self.get_by_id(bus_id)

    def update_status(self, bus_id: int, status: str) -> bool:
        """
        Update only the status of a bus using PostgreSQL function.

        Args:
            bus_id: Bus ID
            status: New status value

        Returns:
            True if update successful, False otherwise
        """
        query = 'SELECT fn_update_bus_status(%s, %s) AS result'
        result = self._execute_query(query, (bus_id, status), fetch_one=True)
        return result.get('result', False) if result else False

    def update_location(self, bus_id: int, latitude: float, longitude: float) -> bool:
        """
        Update bus current location using PostgreSQL function.

        Args:
            bus_id: Bus ID
            latitude: Latitude coordinate
            longitude: Longitude coordinate

        Returns:
            True if update successful, False otherwise
        """
        query = 'SELECT fn_update_bus_location(%s, %s, %s) AS result'
        result = self._execute_query(query, (bus_id, latitude, longitude), fetch_one=True)
        return result.get('result', False) if result else True  # Function returns BOOLEAN

    def assign_to_route(self, bus_id: int, route_id: int) -> bool:
        """
        Assign bus to a route using PostgreSQL function.

        Args:
            bus_id: Bus ID
            route_id: Route ID

        Returns:
            True if assignment successful, False otherwise
        """
        query = 'SELECT fn_assign_bus_to_route(%s, %s) AS result'
        result = self._execute_query(query, (bus_id, route_id), fetch_one=True)
        return result.get('result', False) if result else True  # Function returns BOOLEAN

    # Delete
    def delete(self, bus_id: int) -> bool:
        """
        Hard delete a bus (use with caution).

        Args:
            bus_id: Bus ID

        Returns:
            True if deletion successful, False otherwise
        """
        query = 'DELETE FROM Buses WHERE bus_id = %s'
        try:
            self._db.execute(query, (bus_id,))
            return True
        except Exception:
            return False

    # Business-specific queries
    def count_active_buses(self) -> int:
        """
        Count active buses using PostgreSQL function.

        Returns:
            Number of active buses
        """
        query = 'SELECT fn_get_active_buses_count() AS count'
        result = self._execute_query(query, (), fetch_one=True)
        return result.get('count', 0) if result else 0

    def is_bus_on_route(self, bus_id: int, tolerance_meters: int = 100) -> bool:
        """
        Check if bus is within tolerance of its assigned route using PostgreSQL function.

        Args:
            bus_id: Bus ID
            tolerance_meters: Distance tolerance in meters

        Returns:
            True if bus is on route, False otherwise
        """
        query = 'SELECT fn_is_bus_on_route(%s, %s) AS result'
        result = self._execute_query(query, (bus_id, tolerance_meters), fetch_one=True)
        return result.get('result', False) if result else False

    def get_bus_location_details(self, bus_id: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed location information for a bus using PostgreSQL function.

        Args:
            bus_id: Bus ID

        Returns:
            Dict with location details or None
        """
        query = 'SELECT * FROM fn_get_bus_location_details(%s)'
        return self._execute_query(query, (bus_id,), fetch_one=True)
