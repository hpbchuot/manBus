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
"""
import logging
from typing import Optional

from app.config.database import Database
from app.repositories.user_repository import UserRepository
from app.repositories.auth_repository import AuthRepository
from app.services.auth.password_service import PasswordService
from app.services.auth.token_service import TokenService
from app.services.auth.auth_service import AuthService
from app.services.user.user_service import UserService

logger = logging.getLogger(__name__)


class ServiceFactory:
    """
    Service factory for creating and managing service instances.

    Implements lazy-loading singleton pattern:
    - Services are created only when first requested
    - Same instance is returned on subsequent requests
    - Ensures proper dependency injection
    """

    def __init__(self, db: Database):
        """
        Initialize service factory.

        Args:
            db: Database instance for repository creation
        """
        self.db = db

        # Lazy-loaded repository instances
        self._user_repository: Optional[UserRepository] = None
        self._auth_repository: Optional[AuthRepository] = None

        # Lazy-loaded service instances
        self._password_service: Optional[PasswordService] = None
        self._token_service: Optional[TokenService] = None
        self._auth_service: Optional[AuthService] = None
        self._user_service: Optional[UserService] = None

        logger.info("ServiceFactory initialized")

    # Repository getters

    def get_user_repository(self) -> UserRepository:
        """
        Get or create UserRepository instance.

        Returns:
            UserRepository singleton
        """
        if self._user_repository is None:
            self._user_repository = UserRepository(self.db)
            logger.debug("UserRepository created")
        return self._user_repository

    def get_auth_repository(self) -> AuthRepository:
        """
        Get or create AuthRepository instance.

        Returns:
            AuthRepository singleton
        """
        if self._auth_repository is None:
            self._auth_repository = AuthRepository(self.db)
            logger.debug("AuthRepository created")
        return self._auth_repository

    # Service getters

    def get_password_service(self) -> PasswordService:
        """
        Get or create PasswordService instance.

        Returns:
            PasswordService singleton (no dependencies)
        """
        if self._password_service is None:
            self._password_service = PasswordService()
            logger.debug("PasswordService created")
        return self._password_service

    def get_token_service(self) -> TokenService:
        """
        Get or create TokenService instance.

        Dependencies: AuthRepository

        Returns:
            TokenService singleton
        """
        if self._token_service is None:
            auth_repo = self.get_auth_repository()
            self._token_service = TokenService(auth_repo)
            logger.debug("TokenService created")
        return self._token_service

    def get_auth_service(self) -> AuthService:
        """
        Get or create AuthService instance.

        Dependencies:
            - UserRepository
            - AuthRepository
            - PasswordService
            - TokenService

        Returns:
            AuthService singleton
        """
        if self._auth_service is None:
            user_repo = self.get_user_repository()
            auth_repo = self.get_auth_repository()
            password_service = self.get_password_service()
            token_service = self.get_token_service()

            self._auth_service = AuthService(
                user_repository=user_repo,
                auth_repository=auth_repo,
                password_service=password_service,
                token_service=token_service
            )
            logger.debug("AuthService created")
        return self._auth_service

    def get_user_service(self) -> UserService:
        """
        Get or create UserService instance.

        Dependencies:
            - UserRepository
            - PasswordService

        Returns:
            UserService singleton
        """
        if self._user_service is None:
            user_repo = self.get_user_repository()
            password_service = self.get_password_service()

            self._user_service = UserService(
                user_repository=user_repo,
                password_service=password_service
            )
            logger.debug("UserService created")
        return self._user_service

    def reset(self):
        """
        Reset all cached instances.
        Useful for testing or when database connection needs refresh.
        """
        self._user_repository = None
        self._auth_repository = None
        self._password_service = None
        self._token_service = None
        self._auth_service = None
        self._user_service = None
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
