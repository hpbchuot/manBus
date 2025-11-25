"""
Service Factory for dependency injection and service initialization.
Provides centralized service creation with lazy loading and singleton pattern.

Usage:
    from app.config.database import Database
    from app.services.factory import ServiceFactory

    db = Database()
    factory = ServiceFactory(db)

    # Get services
    auth_service = factory.get_auth_service()
    user_service = factory.get_user_service()
    bus_service = factory.get_bus_service()

Follows SOLID principles:
- SRP: Single responsibility - service creation and management
- OCP: Open/Closed - extensible via service registration
- DIP: Depends on abstractions (interfaces)
"""
import logging
from typing import Optional, Dict, Callable, Any

from app.config.database import Database
from app.repositories.user_repository import UserRepository
from app.repositories.auth_repository import AuthRepository
from app.repositories.bus_repository import BusRepository
from app.repositories.driver_repository import DriverRepository
from app.repositories.route_repository import RouteRepository, StopRepository
from app.services.auth.token_service import TokenService
from app.services.auth.auth_service import AuthService
from app.services.user.user_service import UserService
from app.services.bus.bus_service import BusService
# from app.services.auth.blacklist_service import BlacklistService
from app.services.driver.driver_service import DriverService
from app.services.route.route_service import RouteService, StopService

logger = logging.getLogger(__name__)


class ServiceFactory:
    """
    Service factory for creating and managing service instances.

    Implements lazy-loading singleton pattern with service registration (OCP):
    - Services are created only when first requested
    - Same instance is returned on subsequent requests
    - Ensures proper dependency injection
    - Extensible via service registration pattern
    """

    def __init__(self, db: Database):
        """
        Initialize service factory.

        Args:
            db: Database instance for repository creation
        """
        self.db = db

        # Cache for instantiated repositories and services
        self._repositories: Dict[str, Any] = {}
        self._services: Dict[str, Any] = {}
        self._service_creators: Dict[str, Callable] = {}

        # Register service creators (OCP - single place to add new services)
        self._register_service_creators()

        logger.info("ServiceFactory initialized")

    def _register_service_creators(self):
        """
        Register how to create each service.
        New services added here - follows Open/Closed Principle.
        """
        # Repository creators
        self._service_creators['user_repository'] = lambda: UserRepository(self.db)
        self._service_creators['auth_repository'] = lambda: AuthRepository(self.db)
        self._service_creators['bus_repository'] = lambda: BusRepository(self.db)
        self._service_creators['driver_repository'] = lambda: DriverRepository(self.db)
        self._service_creators['route_repository'] = lambda: RouteRepository(self.db)
        self._service_creators['stop_repository'] = lambda: StopRepository(self.db)

        # Service creators
        self._service_creators['token_service'] = lambda: TokenService(
            auth_repository=self.get('auth_repository')
        )
        self._service_creators['auth_service'] = lambda: AuthService(
            user_repository=self.get('user_repository'),
            auth_repository=self.get('auth_repository'),
            token_service=self.get('token_service')
        )
        self._service_creators['user_service'] = lambda: UserService(
            user_repository=self.get('user_repository')
        )
        self._service_creators['bus_service'] = lambda: BusService(
            bus_repository=self.get('bus_repository')
        )
        self._service_creators['driver_service'] = lambda: DriverService(
            driver_repository=self.get('driver_repository')
        )
        self._service_creators['route_service'] = lambda: RouteService(
            route_repository=self.get('route_repository')
        )
        self._service_creators['stop_service'] = lambda: StopService(
            stop_repository=self.get('stop_repository')
        )

    def get(self, service_name: str) -> Any:
        """
        Get or create service/repository by name.
        Lazy initialization with singleton pattern.

        Args:
            service_name: Name of the service to retrieve

        Returns:
            Service or repository instance

        Raises:
            ValueError: If service name is unknown
        """
        # Check if already created
        if service_name in self._repositories:
            return self._repositories[service_name]
        if service_name in self._services:
            return self._services[service_name]

        # Create if creator exists
        if service_name in self._service_creators:
            instance = self._service_creators[service_name]()

            # Store in appropriate cache
            if 'repository' in service_name:
                self._repositories[service_name] = instance
                logger.debug(f"{service_name} created")
            else:
                self._services[service_name] = instance
                logger.debug(f"{service_name} created")

            return instance

        raise ValueError(f"Unknown service: {service_name}")

    # Convenience getter methods (backward compatibility)

    def get_user_repository(self) -> UserRepository:
        """Get or create UserRepository instance"""
        return self.get('user_repository')

    def get_auth_repository(self) -> AuthRepository:
        """Get or create AuthRepository instance"""
        return self.get('auth_repository')

    def get_bus_repository(self) -> BusRepository:
        """Get or create BusRepository instance"""
        return self.get('bus_repository')

    def get_driver_repository(self) -> DriverRepository:
        """Get or create DriverRepository instance"""
        return self.get('driver_repository')

    def get_route_repository(self) -> RouteRepository:
        """Get or create RouteRepository instance"""
        return self.get('route_repository')

    def get_stop_repository(self) -> StopRepository:
        """Get or create StopRepository instance"""
        return self.get('stop_repository')

    def get_token_service(self) -> TokenService:
        """Get or create TokenService instance"""
        return self.get('token_service')

    def get_auth_service(self) -> AuthService:
        """Get or create AuthService instance"""
        return self.get('auth_service')

    def get_user_service(self) -> UserService:
        """Get or create UserService instance"""
        return self.get('user_service')

    def get_bus_service(self) -> BusService:
        """Get or create BusService instance"""
        return self.get('bus_service')

    def get_driver_service(self) -> DriverService:
        """Get or create DriverService instance"""
        return self.get('driver_service')

    def get_route_service(self) -> RouteService:
        """Get or create RouteService instance"""
        return self.get('route_service')

    def get_stop_service(self) -> StopService:
        """Get or create StopService instance"""
        return self.get('stop_service')

    def reset(self):
        """
        Reset all cached instances.
        Useful for testing or when database connection needs refresh.
        """
        self._repositories.clear()
        self._services.clear()
        logger.info("ServiceFactory reset - all instances cleared")


# Global factory instance (optional convenience)
_global_factory: Optional[ServiceFactory] = None


def get_factory(db: Optional[Database] = None) -> ServiceFactory:
    """
    Get global ServiceFactory instance.

    Args:
        db: Database instance (required on first call)

    Returns:
        Global ServiceFactory instance

    Raises:
        ValueError: If db is None and factory not yet initialized
    """
    global _global_factory

    if _global_factory is None:
        if db is None:
            raise ValueError("Database instance required to initialize factory")
        _global_factory = ServiceFactory(db)
        logger.info("Global ServiceFactory initialized")

    return _global_factory


def reset_factory():
    """
    Reset global factory instance.
    Useful for testing.
    """
    global _global_factory
    if _global_factory:
        _global_factory.reset()
    _global_factory = None
    logger.info("Global ServiceFactory reset")
