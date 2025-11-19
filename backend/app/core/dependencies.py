"""
Dependency Injection Container
Manual dependency injection following the Dependency Inversion Principle
"""
from app.repositories.user_repository import UserRepository
from app.services.auth.strategies.jwt_strategy import JWTAuthenticationStrategy
from app.services.auth.blacklist_service import BlacklistService
from app.services.auth.auth_service import AuthService
from app.config import JWT_SECRET_KEY


class DependencyContainer:
    """Container for managing application dependencies"""

    def __init__(self, db_executor):
        """
        Initialize dependency container

        Args:
            db_executor: Database connection/executor
        """
        self._db = db_executor
        self._instances = {}

    def get_user_repository(self):
        """Get or create UserRepository instance"""
        if 'user_repository' not in self._instances:
            self._instances['user_repository'] = UserRepository(self._db)
        return self._instances['user_repository']

    def get_jwt_strategy(self):
        """Get or create JWT authentication strategy"""
        if 'jwt_strategy' not in self._instances:
            self._instances['jwt_strategy'] = JWTAuthenticationStrategy(
                secret_key=JWT_SECRET_KEY,
                algorithm='HS256',
                token_expiry_hours=24
            )
        return self._instances['jwt_strategy']

    def get_blacklist_service(self):
        """Get or create BlacklistService instance"""
        if 'blacklist_service' not in self._instances:
            self._instances['blacklist_service'] = BlacklistService(self._db)
        return self._instances['blacklist_service']

    def get_auth_service(self):
        """Get or create AuthService with all dependencies"""
        if 'auth_service' not in self._instances:
            self._instances['auth_service'] = AuthService(
                user_repository=self.get_user_repository(),
                auth_strategy=self.get_jwt_strategy(),
                blacklist_service=self.get_blacklist_service()
            )
        return self._instances['auth_service']

    def clear_instances(self):
        """Clear all cached instances (useful for testing)"""
        self._instances.clear()


# Global container instance (will be initialized in main.py)
_container = None


def init_container(db_executor):
    """Initialize the global dependency container"""
    global _container
    _container = DependencyContainer(db_executor)
    return _container
