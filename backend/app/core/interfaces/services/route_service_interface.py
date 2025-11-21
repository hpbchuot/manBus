from abc import ABC, abstractmethod
from typing import Optional, List
from app.schemas.route_schemas import (
    RouteResponse, RouteDetailResponse, RouteCreate, RouteUpdate,
    StopResponse, StopCreate, StopUpdate, RouteStopCreate
)


class IRouteService(ABC):
    """
    Interface for Route Service following Interface Segregation Principle (ISP).
    Defines contract for route-related business operations.
    """

    @abstractmethod
    def get_by_id(self, route_id: int) -> Optional[RouteDetailResponse]:
        """
        Get route by ID with stops information.

        Args:
            route_id: Route ID

        Returns:
            RouteDetailResponse or None if not found
        """
        pass

    @abstractmethod
    def get_by_name(self, route_name: str) -> Optional[RouteResponse]:
        """
        Get route by name.

        Args:
            route_name: Route name

        Returns:
            RouteResponse or None if not found
        """
        pass

    @abstractmethod
    def get_all_active(self) -> List[RouteResponse]:
        """
        Get all active routes.

        Returns:
            List of active routes
        """
        pass

    @abstractmethod
    def get_all(self) -> List[RouteResponse]:
        """
        Get all routes.

        Returns:
            List of all routes
        """
        pass

    @abstractmethod
    def get_routes_with_buses(self) -> List[dict]:
        """
        Get routes with assigned bus count.

        Returns:
            List of routes with bus count information
        """
        pass

    @abstractmethod
    def create(self, route_data: RouteCreate) -> Optional[RouteResponse]:
        """
        Create new route with validation.

        Args:
            route_data: Route creation data

        Returns:
            Created RouteResponse or None if creation failed
        """
        pass

    @abstractmethod
    def update(self, route_id: int, route_data: RouteUpdate) -> Optional[RouteResponse]:
        """
        Update route information.

        Args:
            route_id: Route ID
            route_data: Updated route data

        Returns:
            Updated RouteResponse or None if update failed
        """
        pass

    @abstractmethod
    def delete(self, route_id: int) -> bool:
        """
        Delete route.

        Args:
            route_id: Route ID

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def add_stop_to_route(self, stop_data: RouteStopCreate) -> bool:
        """
        Add a stop to a route.

        Args:
            stop_data: Stop and route association data

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def remove_stop_from_route(self, route_id: int, stop_id: int) -> bool:
        """
        Remove a stop from a route.

        Args:
            route_id: Route ID
            stop_id: Stop ID

        Returns:
            True if successful, False otherwise
        """
        pass


class IStopService(ABC):
    """
    Interface for Stop Service.
    Separated from IRouteService to follow ISP.
    """

    @abstractmethod
    def get_by_id(self, stop_id: int) -> Optional[StopResponse]:
        """
        Get stop by ID.

        Args:
            stop_id: Stop ID

        Returns:
            StopResponse or None if not found
        """
        pass

    @abstractmethod
    def get_all(self) -> List[StopResponse]:
        """
        Get all stops.

        Returns:
            List of all stops
        """
        pass

    @abstractmethod
    def create(self, stop_data: StopCreate) -> Optional[StopResponse]:
        """
        Create new stop.

        Args:
            stop_data: Stop creation data

        Returns:
            Created StopResponse or None if creation failed
        """
        pass

    @abstractmethod
    def update(self, stop_id: int, stop_data: StopUpdate) -> Optional[StopResponse]:
        """
        Update stop information.

        Args:
            stop_id: Stop ID
            stop_data: Updated stop data

        Returns:
            Updated StopResponse or None if update failed
        """
        pass

    @abstractmethod
    def delete(self, stop_id: int) -> bool:
        """
        Delete stop.

        Args:
            stop_id: Stop ID

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def find_nearby_stops(self, latitude: float, longitude: float, radius_km: float = 1.0, limit: int = 10) -> List[StopResponse]:
        """
        Find stops near a location.

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            radius_km: Search radius in kilometers
            limit: Maximum results

        Returns:
            List of nearby stops
        """
        pass
