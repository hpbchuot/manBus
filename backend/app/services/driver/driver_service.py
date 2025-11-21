"""
Driver Service - Following SOLID principles.

This service follows all SOLID principles:
- SRP: Only driver-related business logic
- OCP: Extensible via composition
- LSP: Implements IDriverService
- ISP: Focused interface
- DIP: Depends on DriverRepository abstraction
"""
from typing import Optional, List, Dict, Any
from app.repositories.driver_repository import DriverRepository


class DriverService:
    """
    Driver Service - Handles driver business logic.

    Follows SOLID principles:
    - SRP: Only driver-related business logic (no ORM, no token parsing)
    - OCP: Can be extended without modification
    - LSP: Implements service contract
    - ISP: Focused interface with only necessary methods
    - DIP: Depends on DriverRepository abstraction, not concrete ORM
    """

    def __init__(self, driver_repository: DriverRepository):
        """
        Dependency injection - depends on abstraction.

        Args:
            driver_repository: Driver repository instance
        """
        self.repository = driver_repository

    # Create operations
    def create(self, user_id: int, license_number: str, bus_id: int) -> Optional[Dict[str, Any]]:
        """
        Create new driver with validation.

        Args:
            user_id: User ID to assign as driver
            license_number: Driver's license number
            bus_id: Bus ID to assign

        Returns:
            Created driver dict or None if creation failed

        Raises:
            ValueError: If validation fails
        """
        # Business validation
        if not license_number or len(license_number.strip()) < 5:
            raise ValueError("License number must be at least 5 characters")

        # Check if user is already a driver
        if self.repository.is_user_driver(user_id):
            raise ValueError(f"User {user_id} is already a driver")

        # Create via repository
        entity_dict = self.repository.create({
            'user_id': user_id,
            'license_number': license_number.strip(),
            'bus_id': bus_id
        })

        return entity_dict

    # Read operations
    def get_by_id(self, driver_id: int) -> Optional[Dict[str, Any]]:
        """
        Get driver by ID.

        Args:
            driver_id: Driver ID

        Returns:
            Driver dict or None if not found
        """
        return self.repository.get_by_id(driver_id)

    def get_by_user_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get driver by user ID.

        Args:
            user_id: User ID

        Returns:
            Driver dict with bus and route information or None if not found
        """
        return self.repository.get_by_user_id(user_id)

    def get_by_bus_id(self, bus_id: int) -> Optional[Dict[str, Any]]:
        """
        Get driver assigned to a specific bus.

        Args:
            bus_id: Bus ID

        Returns:
            Driver dict or None if not found
        """
        return self.repository.get_by_bus_id(bus_id)

    def get_all_active(self) -> List[Dict[str, Any]]:
        """
        Get all active drivers.

        Returns:
            List of active driver dicts with user, bus, and route information
        """
        return self.repository.get_all_active()

    def get_all(self, include_deleted_users: bool = False) -> List[Dict[str, Any]]:
        """
        Get all drivers.

        Args:
            include_deleted_users: If True, include drivers whose users are deleted

        Returns:
            List of driver dicts
        """
        return self.repository.get_all(include_deleted_users)

    def get_drivers_on_route(self, route_id: int) -> List[Dict[str, Any]]:
        """
        Get all drivers assigned to buses on a specific route.

        Args:
            route_id: Route ID

        Returns:
            List of driver dicts with bus and route information
        """
        return self.repository.get_drivers_on_route(route_id)

    def is_user_driver(self, user_id: int) -> bool:
        """
        Check if a user is a driver.

        Args:
            user_id: User ID to check

        Returns:
            True if user is a driver, False otherwise
        """
        return self.repository.is_user_driver(user_id)

    def get_driver_count(self, status: Optional[str] = None) -> int:
        """
        Get count of drivers by status.

        Args:
            status: Optional status filter (Active, Inactive, Suspended)

        Returns:
            Number of drivers
        """
        return self.repository.get_driver_count(status)

    # Update operations
    def update_status(self, driver_id: int, status: str) -> bool:
        """
        Update driver status.

        Args:
            driver_id: Driver ID
            status: New status (Active, Inactive, Suspended)

        Returns:
            True if update successful

        Raises:
            ValueError: If validation fails
        """
        # Business validation
        valid_statuses = ['Active', 'Inactive', 'Suspended']
        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")

        # Check existence
        driver = self.repository.get_by_id(driver_id)
        if not driver:
            raise ValueError(f"Driver {driver_id} not found")

        # Update via repository
        success = self.repository.update_status(driver_id, status)
        if not success:
            raise ValueError(f"Failed to update driver {driver_id} status")

        return True

    def update_license(self, driver_id: int, new_license: str) -> bool:
        """
        Update driver's license number.

        Args:
            driver_id: Driver ID
            new_license: New license number

        Returns:
            True if update successful

        Raises:
            ValueError: If validation fails
        """
        # Business validation
        if not new_license or len(new_license.strip()) < 5:
            raise ValueError("License number must be at least 5 characters")

        # Check existence
        driver = self.repository.get_by_id(driver_id)
        if not driver:
            raise ValueError(f"Driver {driver_id} not found")

        # Update via repository
        success = self.repository.update_license(driver_id, new_license.strip())
        if not success:
            raise ValueError(f"Failed to update driver {driver_id} license")

        return True

    def assign_to_bus(self, driver_id: int, bus_id: int) -> bool:
        """
        Assign driver to a bus.

        Args:
            driver_id: Driver ID
            bus_id: Bus ID

        Returns:
            True if assignment successful

        Raises:
            ValueError: If validation fails
        """
        # Check existence
        driver = self.repository.get_by_id(driver_id)
        if not driver:
            raise ValueError(f"Driver {driver_id} not found")

        # Business rule: Driver must be active
        if driver.get('status') != 'Active':
            raise ValueError(f"Driver {driver_id} must be active to be assigned to a bus")

        # Assign via repository
        success = self.repository.assign_to_bus(driver_id, bus_id)
        if not success:
            raise ValueError(f"Failed to assign driver {driver_id} to bus {bus_id}")

        return True

    # Delete operations
    def delete(self, driver_id: int) -> bool:
        """
        Delete driver (hard delete - use with caution).

        Args:
            driver_id: Driver ID

        Returns:
            True if deletion successful

        Raises:
            ValueError: If driver not found
        """
        # Check existence
        driver = self.repository.get_by_id(driver_id)
        if not driver:
            raise ValueError(f"Driver {driver_id} not found")

        # Delete via repository
        success = self.repository.delete(driver_id)
        if not success:
            raise ValueError(f"Failed to delete driver {driver_id}")

        return True
