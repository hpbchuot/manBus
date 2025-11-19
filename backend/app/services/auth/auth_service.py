import uuid
from app.core.interfaces.strategies.auth_strategy import IAuthenticationStrategy
from app.core.interfaces.services.auth_service_interface import IAuthService
from app.core.interfaces.repository import IRepository
from app.core.interfaces.services.blacklist_service_interface import IBlacklistService
from app.schemas.user_schemas import User

class AuthService(IAuthService):
    """Authentication service with dependency injection"""

    def __init__(self,
                 user_repository: IRepository,
                 auth_strategy: IAuthenticationStrategy,
                 blacklist_service: IBlacklistService):
        """
        Initialize auth service with dependencies

        Args:
            user_repository: Repository for user data access
            auth_strategy: Strategy for token generation/validation
            blacklist_service: Service for token blacklist management
        """
        self._user_repo = user_repository
        self._auth_strategy = auth_strategy
        self._blacklist = blacklist_service

    def register(self, user_data):
        """Register a new user"""

        # Prepare user entity
        entity = {
            'username': user_data.get('username'),
            'email': user_data.get('email'),
            'password': user_data.get('password'),
            'name': user_data.get('name'),
            'phone': user_data.get('phone'),
            'role': user_data.get('role', 'user')
        }

        # Create user in database
        result = self._user_repo.create(entity)

        if result:
            return User(dict(result[0])) if isinstance(result, list) else User(dict(result))
        return None

    def login(self, credentials):
        """Authenticate user and return token using fn_verify_user_password"""
        # Verify password and get user using database function
        user_data = self._user_repo.verify_password(
            credentials.get('email'),
            credentials.get('password')
        )

        if not user_data:
            raise ValueError("Invalid credentials")

        # Validate that user has required fields
        if not user_data.get('public_id'):
            raise ValueError("User account is invalid - missing public_id")

        # Generate token
        token_data = self._auth_strategy.authenticate({
            'uuid': user_data['public_id'],
            'username': user_data.get('username', '')
        })

        return {
            'token': token_data['token'],
            'expires_in': token_data['expires_in'],
            'user': User(user_data)
        }

    def logout(self, token):
        """Invalidate token by adding to blacklist"""
        self._blacklist.add_to_blacklist(token)
        return {'message': 'Successfully logged out'}

    def verify_token(self, token):
        """Verify token validity and return user data"""
        # Check if blacklisted
        if self._blacklist.is_blacklisted(token):
            raise ValueError("Token blacklisted")

        # Validate token
        payload = self._auth_strategy.validate_token(token)

        # Get user from database using public_id
        user_data = self._user_repo.get_by_public_id(payload['uuid'])

        if not user_data:
            raise ValueError("User not found")

        return User(user_data)