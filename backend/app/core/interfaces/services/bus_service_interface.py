from abc import ABC, abstractmethod
from typing import Optional, List
from app.schemas.bus_schemas import (
    BusResponse, BusDetailResponse, BusCreate, BusUpdate,
    BusLocationUpdate, BusStatusUpdate, BusRouteAssignment
)


class IBusService(ABC):
    """
    Interface for Bus Service following Interface Segregation Principle (ISP).
    Defines contract for bus-related business operations.
    """

    @abstractmethod
    def get_by_id(self, bus_id: int) -> Optional[BusDetailResponse]:
        """
        Get bus by ID with route information.

        Args:
            bus_id: Bus ID

        Returns:
            BusDetailResponse or None if not found
        """
        pass

    @abstractmethod
    def get_by_plate_number(self, plate_number: str) -> Optional[BusResponse]:
        """
        Get bus by plate number.

        Args:
            plate_number: Vehicle plate number

        Returns:
            BusResponse or None if not found
        """
        pass

    @abstractmethod
    def get_all_active(self) -> List[BusResponse]:
        """
        Get all active buses.

        Returns:
            List of active buses
        """
        pass

    @abstractmethod
    def get_all(self, include_inactive: bool = False) -> List[BusResponse]:
        """
        Get all buses.

        Args:
            include_inactive: Include inactive/maintenance/retired buses

        Returns:
            List of buses
        """
        pass

    @abstractmethod
    def create(self, bus_data: BusCreate) -> Optional[BusResponse]:
        """
        Create new bus with validation.

        Args:
            bus_data: Bus creation data

        Returns:
            Created BusResponse or None if creation failed
        """
        pass

    @abstractmethod
    def update(self, bus_id: int, bus_data: BusUpdate) -> Optional[BusResponse]:
        """
        Update bus information.

        Args:
            bus_id: Bus ID
            bus_data: Updated bus data

        Returns:
            Updated BusResponse or None if update failed
        """
        pass

    @abstractmethod
    def update_status(self, bus_id: int, status_data: BusStatusUpdate) -> bool:
        """
        Update bus status.

        Args:
            bus_id: Bus ID
            status_data: New status

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def update_location(self, bus_id: int, location_data: BusLocationUpdate) -> bool:
        """
        Update bus location (real-time tracking).

        Args:
            bus_id: Bus ID
            location_data: New location coordinates

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def delete(self, bus_id: int) -> bool:
        """
        Delete bus.

        Args:
            bus_id: Bus ID

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def assign_to_route(self, bus_id: int, assignment: BusRouteAssignment) -> bool:
        """
        Assign bus to a route with validation.

        Args:
            bus_id: Bus ID
            assignment: Route assignment data

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def get_buses_by_route(self, route_id: int) -> List[BusResponse]:
        """
        Get all buses on a specific route.

        Args:
            route_id: Route ID

        Returns:
            List of buses on the route
        """
        pass

    @abstractmethod
    def find_nearest_buses(self, latitude: float, longitude: float, route_id: Optional[int] = None, limit: int = 5) -> List[dict]:
        """
        Find nearest buses to a location.

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            route_id: Optional route filter
            limit: Maximum results

        Returns:
            List of nearest buses with distance
        """
        pass
