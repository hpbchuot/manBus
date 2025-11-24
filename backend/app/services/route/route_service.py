"""
Route Service - Following SOLID principles.

This service follows all SOLID principles:
- SRP: Only route-related business logic
- OCP: Extensible via composition
- LSP: Implements IRouteService
- ISP: Focused interface
- DIP: Depends on RouteRepository abstraction
"""
from typing import Optional, List, Dict, Any
from app.repositories.route_repository import RouteRepository, StopRepository


class RouteService:
    """
    Route Service - Handles route business logic.

    Follows SOLID principles:
    - SRP: Only route-related business logic (no ORM, no token parsing)
    - OCP: Can be extended without modification
    - LSP: Implements service contract
    - ISP: Focused interface with only necessary methods
    - DIP: Depends on RouteRepository abstraction, not concrete ORM
    """

    def __init__(self, route_repository: RouteRepository):
        """
        Dependency injection - depends on abstraction.

        Args:
            route_repository: Route repository instance
        """
        self.repository = route_repository

    # Create operations
    def create(self, name: str, coordinates: Any) -> Optional[Dict[str, Any]]:
        """
        Create new route with validation.

        Args:
            name: Route name
            coordinates: JSONB array of [lat, lon] coordinate pairs

        Returns:
            Created route dict or None if creation failed

        Raises:
            ValueError: If validation fails
        """
        # Business validation
        if not name or len(name.strip()) < 3:
            raise ValueError("Route name must be at least 3 characters")

        # Check for duplicate name
        existing = self.repository.get_by_name(name.strip())
        if existing:
            raise ValueError(f"Route with name '{name}' already exists")

        # Create via repository
        entity_dict = self.repository.create({
            'name': name.strip(),
            'coordinates': coordinates
        })

        return entity_dict

    # Read operations
    def get_by_id(self, route_id: int) -> Optional[Dict[str, Any]]:
        """
        Get route by ID.

        Args:
            route_id: Route ID

        Returns:
            Route dict or None if not found
        """
        return self.repository.get_by_id(route_id)

    def get_by_name(self, route_name: str) -> Optional[Dict[str, Any]]:
        """
        Get route by name.

        Args:
            route_name: Route name to search

        Returns:
            Route dict or None if not found
        """
        return self.repository.get_by_name(route_name)

    def get_all(self) -> List[Dict[str, Any]]:
        """
        Get all routes with stop count and length.

        Returns:
            List of route dicts
        """
        return self.repository.get_all()

    def get_stops_on_route(self, route_id: int) -> List[Dict[str, Any]]:
        """
        Get all stops for a route ordered by sequence.

        Args:
            route_id: Route ID

        Returns:
            List of stop dicts with sequence and location

        Raises:
            ValueError: If route not found
        """
        # Check existence
        route = self.repository.get_by_id(route_id)
        if not route:
            raise ValueError(f"Route {route_id} not found")

        return self.repository.get_stops_on_route(route_id)

    def get_route_length(self, route_id: int) -> float:
        """
        Calculate route length in meters.

        Args:
            route_id: Route ID

        Returns:
            Route length in meters

        Raises:
            ValueError: If route not found
        """
        # Check existence
        route = self.repository.get_by_id(route_id)
        if not route:
            raise ValueError(f"Route {route_id} not found")

        return self.repository.get_route_length(route_id)

    def get_route_geojson(self, route_id: int) -> Optional[Dict[str, Any]]:
        """
        Get route geometry as GeoJSON.

        Args:
            route_id: Route ID

        Returns:
            GeoJSON dict or None

        Raises:
            ValueError: If route not found
        """
        # Check existence
        route = self.repository.get_by_id(route_id)
        if not route:
            raise ValueError(f"Route {route_id} not found")

        return self.repository.get_route_geojson(route_id)

    def find_routes_near_location(
        self,
        latitude: float,
        longitude: float,
        radius_meters: int = 500
    ) -> List[Dict[str, Any]]:
        """
        Find routes passing near a location.

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            radius_meters: Search radius in meters

        Returns:
            List of route dicts with distance information
        """
        # Business validation
        if radius_meters < 1:
            raise ValueError("Radius must be at least 1 meter")

        if radius_meters > 10000:
            raise ValueError("Radius cannot exceed 10000 meters")

        return self.repository.find_routes_near_location(latitude, longitude, radius_meters)

    def find_nearest_stops(
        self,
        latitude: float,
        longitude: float,
        radius_meters: int = 1000,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find stops within a radius of a location.

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            radius_meters: Search radius in meters
            limit: Maximum number of results

        Returns:
            List of stop dicts with distance information
        """
        # Business validation
        if radius_meters < 1:
            raise ValueError("Radius must be at least 1 meter")

        if limit < 1:
            raise ValueError("Limit must be at least 1")

        return self.repository.find_nearest_stops(latitude, longitude, radius_meters, limit)

    def is_point_on_route(
        self,
        route_id: int,
        latitude: float,
        longitude: float,
        tolerance_meters: int = 100
    ) -> bool:
        """
        Check if a point is within tolerance of a route.

        Args:
            route_id: Route ID
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            tolerance_meters: Distance tolerance in meters

        Returns:
            True if point is on route, False otherwise

        Raises:
            ValueError: If route not found
        """
        # Check existence
        route = self.repository.get_by_id(route_id)
        if not route:
            raise ValueError(f"Route {route_id} not found")

        return self.repository.is_point_on_route(route_id, latitude, longitude, tolerance_meters)

    # Update operations
    def update(self, route_id: int, name: Optional[str] = None, coordinates: Any = None) -> Optional[Dict[str, Any]]:
        """
        Update route information.

        Args:
            route_id: Route ID
            name: Optional new route name
            coordinates: Optional new coordinates

        Returns:
            Updated route dict or None

        Raises:
            ValueError: If validation fails
        """
        # Check existence
        route = self.repository.get_by_id(route_id)
        if not route:
            raise ValueError(f"Route {route_id} not found")

        # Build update dict
        update_data = {}
        if name is not None:
            if len(name.strip()) < 3:
                raise ValueError("Route name must be at least 3 characters")

            # Check for duplicate name (excluding current route)
            existing = self.repository.get_by_name(name.strip())
            if existing and existing.get('id') != route_id:
                raise ValueError(f"Route with name '{name}' already exists")

            update_data['name'] = name.strip()

        if coordinates is not None:
            update_data['coordinates'] = coordinates

        if not update_data:
            return route

        # Update via repository
        return self.repository.update(route_id, update_data)

    def update_geometry(self, route_id: int, coordinates: Any) -> bool:
        """
        Update route geometry.

        Args:
            route_id: Route ID
            coordinates: JSONB array of [lat, lon] pairs

        Returns:
            True if update successful

        Raises:
            ValueError: If route not found
        """
        # Check existence
        route = self.repository.get_by_id(route_id)
        if not route:
            raise ValueError(f"Route {route_id} not found")

        # Update via repository
        success = self.repository.update_geometry(route_id, coordinates)
        if not success:
            raise ValueError(f"Failed to update route {route_id} geometry")

        return True

    # Stop management
    def add_stop_to_route(self, route_id: int, stop_id: int, sequence: int = 0) -> bool:
        """
        Add a stop to a route.

        Args:
            route_id: Route ID
            stop_id: Stop ID
            sequence: Stop sequence number

        Returns:
            True if successful

        Raises:
            ValueError: If validation fails
        """
        # Check route existence
        route = self.repository.get_by_id(route_id)
        if not route:
            raise ValueError(f"Route {route_id} not found")

        # Add stop via repository
        success = self.repository.add_stop_to_route(route_id, stop_id, sequence)
        if not success:
            raise ValueError(f"Failed to add stop {stop_id} to route {route_id}")

        return True

    def remove_stop_from_route(self, route_id: int, stop_id: int) -> bool:
        """
        Remove a stop from a route.

        Args:
            route_id: Route ID
            stop_id: Stop ID

        Returns:
            True if successful

        Raises:
            ValueError: If validation fails
        """
        # Check route existence
        route = self.repository.get_by_id(route_id)
        if not route:
            raise ValueError(f"Route {route_id} not found")

        # Remove stop via repository
        success = self.repository.remove_stop_from_route(route_id, stop_id)
        if not success:
            raise ValueError(f"Failed to remove stop {stop_id} from route {route_id}")

        return True

    def reorder_route_stops(self, route_id: int, stop_sequences: Any) -> bool:
        """
        Update stop sequences for a route.

        Args:
            route_id: Route ID
            stop_sequences: JSONB array of objects with stop_id and sequence

        Returns:
            True if successful

        Raises:
            ValueError: If validation fails
        """
        # Check route existence
        route = self.repository.get_by_id(route_id)
        if not route:
            raise ValueError(f"Route {route_id} not found")

        # Reorder via repository
        success = self.repository.reorder_route_stops(route_id, stop_sequences)
        if not success:
            raise ValueError(f"Failed to reorder stops for route {route_id}")

        return True

    # Delete operations
    def delete(self, route_id: int) -> bool:
        """
        Delete route (hard delete - use with caution).

        Args:
            route_id: Route ID

        Returns:
            True if deletion successful

        Raises:
            ValueError: If route not found
        """
        # Check existence
        route = self.repository.get_by_id(route_id)
        if not route:
            raise ValueError(f"Route {route_id} not found")

        # Delete via repository
        success = self.repository.delete(route_id)
        if not success:
            raise ValueError(f"Failed to delete route {route_id}")

        return True


class StopService:
    """
    Stop Service - Handles bus stop business logic.

    Follows SOLID principles:
    - SRP: Only stop-related business logic
    - OCP: Can be extended without modification
    - LSP: Implements service contract
    - ISP: Focused interface with only necessary methods
    - DIP: Depends on StopRepository abstraction
    """

    def __init__(self, stop_repository: StopRepository):
        """
        Dependency injection - depends on abstraction.

        Args:
            stop_repository: Stop repository instance
        """
        self.repository = stop_repository

    # Create operations
    def create(self, name: str, latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
        """
        Create new stop with validation.

        Args:
            name: Stop name
            latitude: Latitude coordinate
            longitude: Longitude coordinate

        Returns:
            Created stop dict or None if creation failed

        Raises:
            ValueError: If validation fails
        """
        # Business validation
        if not name or len(name.strip()) < 3:
            raise ValueError("Stop name must be at least 3 characters")

        # Validate coordinates
        if latitude < -90 or latitude > 90:
            raise ValueError("Latitude must be between -90 and 90")

        if longitude < -180 or longitude > 180:
            raise ValueError("Longitude must be between -180 and 180")

        # Create via repository
        entity_dict = self.repository.create({
            'name': name.strip(),
            'latitude': latitude,
            'longitude': longitude
        })

        return entity_dict

    # Read operations
    def get_by_id(self, stop_id: int) -> Optional[Dict[str, Any]]:
        """
        Get stop by ID.

        Args:
            stop_id: Stop ID

        Returns:
            Stop dict or None if not found
        """
        return self.repository.get_by_id(stop_id)

    def get_all(self) -> List[Dict[str, Any]]:
        """
        Get all stops.

        Returns:
            List of stop dicts
        """
        return self.repository.get_all()

    # Update operations
    def update(self, stop_id: int, name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Update stop information.

        Args:
            stop_id: Stop ID
            name: Optional new stop name

        Returns:
            Updated stop dict or None

        Raises:
            ValueError: If validation fails
        """
        # Check existence
        stop = self.repository.get_by_id(stop_id)
        if not stop:
            raise ValueError(f"Stop {stop_id} not found")

        # Build update dict
        update_data = {}
        if name is not None:
            if len(name.strip()) < 3:
                raise ValueError("Stop name must be at least 3 characters")
            update_data['name'] = name.strip()

        if not update_data:
            return stop

        # Update via repository
        return self.repository.update(stop_id, update_data)

    # Delete operations
    def delete(self, stop_id: int) -> bool:
        """
        Delete stop (hard delete - use with caution).

        Args:
            stop_id: Stop ID

        Returns:
            True if deletion successful

        Raises:
            ValueError: If stop not found
        """
        # Check existence
        stop = self.repository.get_by_id(stop_id)
        if not stop:
            raise ValueError(f"Stop {stop_id} not found")

        # Delete via repository
        success = self.repository.delete(stop_id)
        if not success:
            raise ValueError(f"Failed to delete stop {stop_id}")

        return True
