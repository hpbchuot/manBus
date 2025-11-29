from typing import Optional, List, Dict, Any
from .base_repository import BaseRepository


class RouteRepository(BaseRepository):
    """
    Repository for Route entity.
    Encapsulates all data access logic for routes using PostgreSQL functions.
    Follows Repository Pattern and DIP (Dependency Inversion Principle).
    """

    def _get_table_name(self) -> str:
        """Return the routes table name"""
        return 'Routes'

    def _get_id_column(self) -> str:
        """Return the primary key column name"""
        return 'id'

    # Create
    def create(self, entity: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a new route using PostgreSQL function.

        Args:
            entity: Dict with keys: name (route_name), coordinates (JSONB array)

        Returns:
            Created route as dict or None
        """
        query = 'SELECT fn_create_route(%s, %s) AS result'
        params = (
            entity.get('name'),
            entity.get('coordinates')  # JSONB format
        )
        result = self._execute_query(query, params, fetch_one=True)

        if result and result.get('result'):
            return self.get_by_id(result['result'])
        return None

    # Read operations
    def get_by_id(self, route_id: int) -> Optional[Dict[str, Any]]:
        """
        Get route by ID.

        Args:
            route_id: Route ID

        Returns:
            Route dict or None if not found
        """
        query = 'SELECT * FROM Routes WHERE id = %s'
        return self._execute_query(query, (route_id,), fetch_one=True)

    def get_by_name(self, route_name: str) -> Optional[Dict[str, Any]]:
        """
        Get route by name.

        Args:
            route_name: Route name to search

        Returns:
            Route dict or None if not found
        """
        query = 'SELECT * FROM Routes WHERE name = %s'
        return self._execute_query(query, (route_name,), fetch_one=True)

    def get_all(self) -> List[Dict[str, Any]]:
        """
        Get all routes using PostgreSQL function.

        Returns:
            List of route dicts with stop count and length
        """
        query = 'SELECT * FROM fn_get_all_routes()'
        return self._execute_query(query, (), fetch_one=False)

    def get_stops_on_route(self, route_id: int) -> List[Dict[str, Any]]:
        """
        Get all stops for a route ordered by sequence using PostgreSQL function.

        Args:
            route_id: Route ID

        Returns:
            List of stop dicts with sequence and location
        """
        query = 'SELECT * FROM fn_get_stops_on_route(%s)'
        return self._execute_query(query, (route_id,), fetch_one=False)

    def get_route_length(self, route_id: int) -> float:
        """
        Calculate route length in meters using PostgreSQL function.

        Args:
            route_id: Route ID

        Returns:
            Route length in meters
        """
        query = 'SELECT fn_get_route_length(%s) AS length'
        result = self._execute_query(query, (route_id,), fetch_one=True)
        return float(result.get('length', 0)) if result else 0.0

    def get_route_geojson(self, route_id: int) -> Optional[Dict[str, Any]]:
        """
        Get route geometry as GeoJSON using PostgreSQL function.

        Args:
            route_id: Route ID

        Returns:
            GeoJSON dict or None
        """
        query = 'SELECT fn_get_route_geojson(%s) AS geojson'
        result = self._execute_query(query, (route_id,), fetch_one=True)
        return result.get('geojson') if result else None

    def find_routes_near_location(
        self,
        latitude: float,
        longitude: float,
        radius_meters: int = 500
    ) -> List[Dict[str, Any]]:
        """
        Find routes passing near a location using PostgreSQL function.

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            radius_meters: Search radius in meters

        Returns:
            List of route dicts with distance information
        """
        query = 'SELECT * FROM fn_find_routes_near_location(%s, %s, %s)'
        return self._execute_query(query, (latitude, longitude, radius_meters), fetch_one=False)

    def find_nearest_stops(
        self,
        latitude: float,
        longitude: float,
        radius_meters: int = 1000,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find stops within a radius of a location using PostgreSQL function.

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            radius_meters: Search radius in meters
            limit: Maximum number of results

        Returns:
            List of stop dicts with distance information
        """
        query = 'SELECT * FROM fn_find_nearest_stops(%s, %s, %s, %s)'
        return self._execute_query(query, (latitude, longitude, radius_meters, limit), fetch_one=False)

    def is_point_on_route(
        self,
        route_id: int,
        latitude: float,
        longitude: float,
        tolerance_meters: int = 100
    ) -> bool:
        """
        Check if a point is within tolerance of a route using PostgreSQL function.

        Args:
            route_id: Route ID
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            tolerance_meters: Distance tolerance in meters

        Returns:
            True if point is on route, False otherwise
        """
        query = 'SELECT fn_is_point_on_route(%s, %s, %s, %s) AS result'
        result = self._execute_query(query, (route_id, latitude, longitude, tolerance_meters), fetch_one=True)
        return result.get('result', False) if result else False

    def find_buses_to_destination(
        self,
        current_latitude: float,
        current_longitude: float,
        destination_latitude: float,
        destination_longitude: float,
        radius_meters: int = 500,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find routes that go from current location to destination using PostgreSQL function.
        Args:

            current_latitude: Current latitude
            current_longitude: Current longitude
            destination_latitude: Destination latitude
            destination_longitude: Destination longitude
            radius_meters: Search radius in meters
            limit: Maximum number of results
        Returns:
            List of route dicts that serve the destination
        """
        query = 'SELECT * FROM fn_find_buses_to_destination(%s, %s, %s, %s, %s, %s)'
        return self._execute_query(
            query,
            (
                current_latitude,
                current_longitude,
                destination_latitude,
                destination_longitude,
                radius_meters,
                limit
            ),
            fetch_one=False
        )
    
    # Update operations
    def update(self, route_id: int, entity: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update route information.

        Args:
            route_id: Route ID
            entity: Dict with updated route data

        Returns:
            Updated route dict or None
        """
        update_fields = []
        params = []

        if 'name' in entity:
            update_fields.append('name = %s')
            params.append(entity['name'])
        if 'coordinates' in entity:
            # Use the update geometry function
            self.update_geometry(route_id, entity['coordinates'])

        if update_fields:
            params.append(route_id)
            query = f"UPDATE Routes SET {', '.join(update_fields)}, updated_at = NOW() WHERE id = %s"
            self._db.execute(query, tuple(params))

        return self.get_by_id(route_id)

    def update_geometry(self, route_id: int, coordinates: Any) -> bool:
        """
        Update route geometry using PostgreSQL function.

        Args:
            route_id: Route ID
            coordinates: JSONB array of [lat, lon] pairs

        Returns:
            True if update successful, False otherwise
        """
        query = 'SELECT fn_update_route_geometry(%s, %s) AS result'
        result = self._execute_query(query, (route_id, coordinates), fetch_one=True)
        return result.get('result', False) if result else True  # Function returns BOOLEAN

    # Stop management
    def add_stop_to_route(self, route_id: int, stop_id: int, sequence: int = 0) -> bool:
        """
        Add a stop to a route using PostgreSQL function.

        Args:
            route_id: Route ID
            stop_id: Stop ID
            sequence: Stop sequence number

        Returns:
            True if successful, False otherwise
        """
        query = 'SELECT fn_add_stop_to_route(%s, %s, %s) AS result'
        result = self._execute_query(query, (route_id, stop_id, sequence), fetch_one=True)
        return result.get('result', False) if result else True  # Function returns BOOLEAN

    def remove_stop_from_route(self, route_id: int, stop_id: int) -> bool:
        """
        Remove a stop from a route using PostgreSQL function.

        Args:
            route_id: Route ID
            stop_id: Stop ID

        Returns:
            True if successful, False otherwise
        """
        query = 'SELECT fn_remove_stop_from_route(%s, %s) AS result'
        result = self._execute_query(query, (route_id, stop_id), fetch_one=True)
        return result.get('result', False) if result else True  # Function returns BOOLEAN

    def reorder_route_stops(self, route_id: int, stop_sequences: Any) -> bool:
        """
        Update stop sequences for a route using PostgreSQL function.

        Args:
            route_id: Route ID
            stop_sequences: JSONB array of objects with stop_id and sequence

        Returns:
            True if successful, False otherwise
        """
        query = 'SELECT fn_reorder_route_stops(%s, %s) AS result'
        result = self._execute_query(query, (route_id, stop_sequences), fetch_one=True)
        return result.get('result', False) if result else True  # Function returns BOOLEAN

    # Delete
    def delete(self, route_id: int) -> bool:
        """
        Hard delete a route (use with caution).

        Args:
            route_id: Route ID

        Returns:
            True if deletion successful, False otherwise
        """
        query = 'DELETE FROM Routes WHERE id = %s'
        try:
            self._db.execute(query, (route_id,))
            return True
        except Exception:
            return False


class StopRepository(BaseRepository):
    """
    Repository for Stop entity.
    Encapsulates all data access logic for bus stops using PostgreSQL functions.
    """

    def _get_table_name(self) -> str:
        """Return the stops table name"""
        return 'Stops'

    def _get_id_column(self) -> str:
        """Return the primary key column name"""
        return 'id'

    # Create
    def create(self, entity: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a new stop using PostgreSQL function.

        Args:
            entity: Dict with keys: name (stop_name), latitude, longitude

        Returns:
            Created stop as dict or None
        """
        query = 'SELECT fn_create_stop(%s, %s, %s) AS result'
        params = (
            entity.get('name'),
            entity.get('latitude'),
            entity.get('longitude')
        )
        result = self._execute_query(query, params, fetch_one=True)

        if result and result.get('result'):
            return self.get_by_id(result['result'])
        return None

    # Read operations
    def get_by_id(self, stop_id: int) -> Optional[Dict[str, Any]]:
        """
        Get stop by ID.

        Args:
            stop_id: Stop ID

        Returns:
            Stop dict or None if not found
        """
        query = 'SELECT * FROM Stops WHERE id = %s'
        return self._execute_query(query, (stop_id,), fetch_one=True)

    def get_all(self) -> List[Dict[str, Any]]:
        """
        Get all stops.

        Returns:
            List of stop dicts
        """
        query = 'SELECT * FROM Stops ORDER BY name'
        return self._execute_query(query, (), fetch_one=False)

    # Update operations
    def update(self, stop_id: int, entity: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update stop information.

        Args:
            stop_id: Stop ID
            entity: Dict with updated stop data

        Returns:
            Updated stop dict or None
        """
        update_fields = []
        params = []

        if 'name' in entity:
            update_fields.append('name = %s')
            params.append(entity['name'])

        if not update_fields:
            return self.get_by_id(stop_id)

        params.append(stop_id)
        query = f"UPDATE Stops SET {', '.join(update_fields)} WHERE id = %s"

        self._db.execute(query, tuple(params))
        return self.get_by_id(stop_id)

    # Delete
    def delete(self, stop_id: int) -> bool:
        """
        Hard delete a stop (use with caution).

        Args:
            stop_id: Stop ID

        Returns:
            True if deletion successful, False otherwise
        """
        query = 'DELETE FROM Stops WHERE id = %s'
        try:
            self._db.execute(query, (stop_id,))
            return True
        except Exception:
            return False
