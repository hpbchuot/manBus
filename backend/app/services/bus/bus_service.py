"""
Bus Service - Refactored to follow SOLID principles.

This service follows all SOLID principles:
- SRP: Only bus-related business logic
- OCP: Extensible via mixins
- LSP: Implements IBusService
- ISP: Focused interface
- DIP: Depends on BusRepository abstraction (not ORM)
"""
from typing import Optional, List, Dict, Any
from app.repositories.bus_repository import BusRepository
from app.schemas.bus_schemas import (
    BusResponse, BusDetailResponse, BusCreate, BusUpdate,
    BusLocationUpdate, BusStatusUpdate, BusRouteAssignment
)
from app.core.interfaces.services.bus_service_interface import IBusService
from app.services.mixins import CrudMixin


class BusService(IBusService):
    """
    Bus Service - Handles bus business logic.

    Follows SOLID principles:
    - SRP: Only bus-related business logic (no ORM, no token parsing)
    - OCP: Can be extended without modification
    - LSP: Implements IBusService contract
    - ISP: Focused interface with only necessary methods
    - DIP: Depends on BusRepository abstraction, not concrete ORM

    Note: We don't use mixins with multiple inheritance to avoid complexity.
    Instead, we compose functionality by delegating to the repository.
    """

    def __init__(self, bus_repository: BusRepository):
        """
        Dependency injection - depends on abstraction.

        Args:
            bus_repository: Bus repository instance
        """
        self.repository = bus_repository

    def _to_schema(self, entity_dict: Dict[str, Any], detail: bool = False) -> BusResponse | BusDetailResponse:
        """
        Convert repository result to Pydantic schema.

        Args:
            entity_dict: Dictionary from repository
            detail: If True, return BusDetailResponse with route info

        Returns:
            BusResponse or BusDetailResponse
        """
        if detail and 'route_name' in entity_dict:
            return BusDetailResponse(**entity_dict)
        return BusResponse(**entity_dict)

    # Implement IBusService interface methods

    def get_by_id(self, bus_id: int) -> Optional[BusDetailResponse]:
        """
        Get bus by ID with route information.

        Args:
            bus_id: Bus ID

        Returns:
            BusDetailResponse or None if not found
        """
        entity_dict = self.repository.get_by_id(bus_id)
        if not entity_dict:
            return None
        
        # Convert to detail response with route info
        return BusDetailResponse(**entity_dict)

    def get_by_plate_number(self, plate_number: str) -> Optional[BusDetailResponse]:
        """
        Get bus by plate number.

        Args:
            plate_number: Vehicle plate number

        Returns:
            BusDetailResponse or None if not found
        """
        entity_dict = self.repository.get_by_plate_number(plate_number)
        return BusDetailResponse(**entity_dict) if entity_dict else None

    def get_all_active(self, cursor: Optional[int] = None, limit: Optional[int] = 10) -> List[BusResponse]:
        """
        Get all active buses.

        Returns:
            List of active buses
        """
        entities = self.repository.get_active_buses(cursor, limit)
        return [BusResponse(**e) for e in entities]

    def get_all(
            self, 
            cursor: Optional[int] = None,
            limit: Optional[int] = 10,
            include_inactive: bool = False) -> List[BusResponse]:
        """
        Get all buses.

        Args:
            include_inactive: Include inactive/maintenance/retired buses

        Returns:
            List of buses
        """
        entities = self.repository.get_all(cursor, limit, include_inactive)
        return [BusResponse(**e) for e in entities]

    def create(self, bus_data: BusCreate) -> Optional[BusResponse]:
        """
        Create new bus with validation.

        Args:
            bus_data: Bus creation data

        Returns:
            Created BusResponse or None if creation failed

        Raises:
            ValueError: If validation fails
        """
        # Business validation: Check for duplicate plate number
        existing = self.repository.get_by_plate_number(bus_data.plate_number)
        if existing:
            raise ValueError(f"Bus with plate number {bus_data.plate_number} already exists")

        # Create via repository
        entity_dict = self.repository.create(bus_data.model_dump())
        return BusResponse(**entity_dict) if entity_dict else None

    def update(self, bus_id: int, bus_data: BusUpdate) -> Optional[BusResponse]:
        """
        Update bus information.

        Args:
            bus_id: Bus ID
            bus_data: Updated bus data

        Returns:
            Updated BusResponse or None if update failed

        Raises:
            ValueError: If bus not found or validation fails
        """
        # Check existence
        if not self.repository.exists(bus_id):
            raise ValueError(f"Bus {bus_id} not found")

        # If plate number is being changed, check for duplicates
        if bus_data.plate_number:
            existing = self.repository.get_by_plate_number(bus_data.plate_number)
            if existing and existing.get('bus_id') != bus_id:
                raise ValueError(f"Plate number {bus_data.plate_number} already in use")

        # Update via repository
        entity_dict = self.repository.update(bus_id, bus_data.model_dump(exclude_unset=True))
        return BusResponse(**entity_dict) if entity_dict else None

    def update_status(self, bus_id: int, status_data: BusStatusUpdate) -> bool:
        """
        Update bus status.

        Args:
            bus_id: Bus ID
            status_data: New status

        Returns:
            True if successful, False otherwise

        Raises:
            ValueError: If bus not found
        """
        if not self.repository.exists(bus_id):
            raise ValueError(f"Bus {bus_id} not found")

        return self.repository.update_status(bus_id, status_data.status)

    def update_location(self, bus_id: int, location_data: BusLocationUpdate) -> bool:
        """
        Update bus location (real-time tracking).

        Args:
            bus_id: Bus ID
            location_data: New location coordinates

        Returns:
            True if successful, False otherwise

        Raises:
            ValueError: If bus not found or not active
        """
        # Business validation: Bus must exist and be active
        bus = self.repository.get_by_id(bus_id)
        if not bus:
            raise ValueError(f"Bus {bus_id} not found")

        if bus.get('status') != 'Active':
            raise ValueError(f"Cannot update location for inactive bus {bus_id}")

        # Update location via repository
        return self.repository.update_location(
            bus_id,
            location_data.location.latitude,
            location_data.location.longitude
        )

    def delete(self, bus_id: int) -> bool:
        """
        Delete bus.

        Args:
            bus_id: Bus ID

        Returns:
            True if successful, False otherwise

        Raises:
            ValueError: If bus not found
        """
        if not self.repository.exists(bus_id):
            raise ValueError(f"Bus {bus_id} not found")

        return self.repository.delete(bus_id)

    def assign_to_route(self, bus_id: int, assignment: BusRouteAssignment) -> bool:
        """
        Assign bus to a route with validation.

        Args:
            bus_id: Bus ID
            assignment: Route assignment data

        Returns:
            True if successful, False otherwise

        Raises:
            ValueError: If validation fails
        """
        # Business validation: Bus must exist
        if not self.repository.exists(bus_id):
            raise ValueError(f"Bus {bus_id} not found")

        # Business rule: Bus must be active
        bus = self.repository.get_by_id(bus_id)
        if bus.get('status') not in ['Active', 'Inactive']:
            raise ValueError(f"Bus {bus_id} cannot be assigned (status: {bus.get('status')})")

        # Assign via repository
        return self.repository.assign_to_route(bus_id, assignment.route_id)

    def get_buses_by_route(self, route_id: int) -> List[BusResponse]:
        """
        Get all buses on a specific route.

        Args:
            route_id: Route ID

        Returns:
            List of buses on the route
        """
        entities = self.repository.get_by_route(route_id)
        return [BusResponse(**e) for e in entities]

    def find_nearest_buses(
        self,
        latitude: float,
        longitude: float,
        route_id: Optional[int] = None,
        limit: int = 5
    ) -> List[dict]:
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
        return self.repository.find_nearest_bus(
            latitude=latitude,
            longitude=longitude,
            route_id=route_id,
            limit=limit
        )

    # Additional business logic methods

    def get_active_buses_count(self) -> int:
        """
        Get count of active buses.

        Returns:
            Number of active buses
        """
        return self.repository.count_active_buses()

    def is_bus_on_route(self, bus_id: int, tolerance_meters: int = 100) -> bool:
        """
        Check if bus is on its assigned route.

        Args:
            bus_id: Bus ID
            tolerance_meters: Distance tolerance in meters

        Returns:
            True if bus is on route, False otherwise

        Raises:
            ValueError: If bus not found
        """
        if not self.repository.exists(bus_id):
            raise ValueError(f"Bus {bus_id} not found")

        return self.repository.is_bus_on_route(bus_id, tolerance_meters)

    def get_bus_location_details(self, bus_id: int) -> Optional[dict]:
        """
        Get detailed location information for a bus.

        Args:
            bus_id: Bus ID

        Returns:
            Dict with location details or None

        Raises:
            ValueError: If bus not found
        """
        if not self.repository.exists(bus_id):
            raise ValueError(f"Bus {bus_id} not found")

        return self.repository.get_bus_location_details(bus_id)
