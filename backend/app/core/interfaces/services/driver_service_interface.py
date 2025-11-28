from abc import ABC, abstractmethod
from typing import Optional, List
from app.schemas.driver_schemas import (
    DriverResponse, DriverDetailResponse, DriverCreate, DriverUpdate,
    DriverBusAssignment, DriverStatusUpdate
)


class IDriverService(ABC):
    """
    Interface for Driver Service following Interface Segregation Principle (ISP).
    Defines contract for driver-related business operations.
    """

    @abstractmethod
    def get_by_id(self, driver_id: int) -> Optional[DriverDetailResponse]:
        """
        Get driver by ID with user and bus information.

        Args:
            driver_id: Driver ID

        Returns:
            DriverDetailResponse or None if not found
        """
        pass

    @abstractmethod
    def get_by_user_id(self, user_id: int) -> Optional[DriverResponse]:
        """
        Get driver by user ID.

        Args:
            user_id: User ID

        Returns:
            DriverResponse or None if not found
        """
        pass

    @abstractmethod
    def get_by_license(self, license_number: str) -> Optional[DriverResponse]:
        """
        Get driver by license number.

        Args:
            license_number: License number

        Returns:
            DriverResponse or None if not found
        """
        pass

    @abstractmethod
    def get_all_active(self) -> List[DriverResponse]:
        """
        Get all active drivers.

        Returns:
            List of active drivers
        """
        pass

    @abstractmethod
    def get_available_drivers(self) -> List[DriverResponse]:
        """
        Get drivers available for assignment.

        Returns:
            List of available drivers
        """
        pass

    @abstractmethod
    def create(self, driver_data: DriverCreate) -> Optional[DriverResponse]:
        """
        Create new driver with validation.

        Args:
            driver_data: Driver creation data

        Returns:
            Created DriverResponse or None if creation failed
        """
        pass

    @abstractmethod
    def update(self, driver_id: int, driver_data: DriverUpdate) -> Optional[DriverResponse]:
        """
        Update driver information.

        Args:
            driver_id: Driver ID
            driver_data: Updated driver data

        Returns:
            Updated DriverResponse or None if update failed
        """
        pass

    @abstractmethod
    def update_status(self, driver_id: int, status_data: DriverStatusUpdate) -> bool:
        """
        Update driver status.

        Args:
            driver_id: Driver ID
            status_data: New status

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def delete(self, driver_id: int) -> bool:
        """
        Delete driver.

        Args:
            driver_id: Driver ID

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def assign_to_bus(self, driver_id: int, assignment: DriverBusAssignment) -> bool:
        """
        Assign driver to a bus with validation.

        Args:
            driver_id: Driver ID
            assignment: Bus assignment data

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def get_driver_assignments(self, driver_id: int) -> List[dict]:
        """
        Get all bus assignments for a driver.

        Args:
            driver_id: Driver ID

        Returns:
            List of assignment records
        """
        pass
