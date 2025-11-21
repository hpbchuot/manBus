"""
Authentication service for user login, registration, and session management.
Uses repository pattern: Repository → Service → Schema → Controller
"""
import logging
from typing import Optional, Dict, Any

from app.repositories.user_repository import UserRepository
from app.repositories.auth_repository import AuthRepository
from app.services.auth.password_service import PasswordService
from app.services.auth.token_service import TokenService
from app.schemas.user_schemas import UserRegister, UserLogin, UserLoginResponse, UserResponse
from app.schemas.auth_schemas import TokenResponse
from app.core.interfaces.services.auth_service_interface import IAuthService

logger = logging.getLogger(__name__)

class AuthService(IAuthService):
    """
    Authentication service handling user authentication operations.

    Flow: Controller → Service → Repository → PostgreSQL Function
    Returns: Pydantic schemas
    """

    def __init__(
        self,
        user_repository: UserRepository,
        auth_repository: AuthRepository,
        password_service: PasswordService,
        token_service: TokenService
    ):
        """
        Initialize authentication service.

        Args:
            user_repository: User repository for user data access
            auth_repository: Auth repository for blacklist operations
            password_service: Password hashing service
            token_service: Token generation/validation service
        """
        self.user_repo = user_repository
        self.auth_repo = auth_repository
        self.password_service = password_service
        self.token_service = token_service

    def register(self, user_data: UserRegister | dict) -> UserLoginResponse | dict:
        """
        Register a new user.

        Args:
            user_data: UserRegister schema or dict with user registration data

        Returns:
            UserLoginResponse with user data and token

        Raises:
            UserAlreadyExistsException: If user already exists
        """
        try:
            # Handle both schema and dict input for backward compatibility
            if isinstance(user_data, dict):
                username = user_data.get('username')
                email = user_data.get('email')
                password = user_data.get('password')
                name = user_data.get('name')
                phone = user_data.get('phone')
            else:
                username = user_data.username
                email = user_data.email
                password = user_data.password
                name = user_data.name
                phone = user_data.phone

            # Check if user already exists using repository
            if self.user_repo.user_exists(email, username):
                raise Exception("User with this email or username already exists")

            # Prepare entity for repository
            entity = {
                'name': name,
                'phone': phone,
                'email': email,
                'username': username,
                'password': password,
                'admin': False
            }

            # Create user via repository
            user_dict = self.user_repo.create(entity)

            if not user_dict:
                raise Exception("Failed to create user")

            # Generate token
            token = self.token_service.generate_token(
                user_id=user_dict['id'],
                username=user_dict['username'],
                public_id=user_dict['public_id'],
                admin=user_dict['admin']
            )

            # Return appropriate format based on input type
            return user_dict, token
        except Exception as e:
            logger.error(f"Error during registration: {e}")
            raise

    def login(self, credentials: UserLogin | dict) -> UserLoginResponse | dict:
        """
        Authenticate user and generate token.

        Args:
            credentials: UserLogin schema or dict with credentials

        Returns:
            UserLoginResponse with user data and token

        Raises:
            InvalidCredentialsException: If credentials are invalid
        """
        try:
            # Handle both schema and dict input
            if isinstance(credentials, dict):
                email = credentials.get('email')
                password = credentials.get('password')
            else:
                email = credentials.email
                password = credentials.password

            # Verify user password using repository function
            userId = self.auth_repo.verify_user_password(email, password)
            if not userId:
                raise Exception("Invalid email or password")
            
            user_dict = self.user_repo.get_by_id(userId)

            # Generate token
            token = self.token_service.generate_token(
                user_id=user_dict['id'],
                username=user_dict['username'],
                public_id=user_dict['public_id'],
                admin=user_dict['admin']
            )

            return user_dict, token
        except Exception as e:
            logger.error(f"Error during login: {e}")
            raise

    def logout(self, token: str) -> bool | dict:
        """
        Logout user by blacklisting their token.

        Args:
            token: JWT token to invalidate

        Returns:
            True if successful, or dict for backward compatibility
        """
        try:
            # Validate token first
            token_data = self.token_service.validate_token(token)
            if not token_data:
                logger.warning("Attempted to logout with invalid token")
                return False

            # Blacklist token via token service (which uses auth_repository)
            success = self.token_service.blacklist_token(token)

            if success:
                logger.info(f"User logged out: {token_data.username}")

            return {'message': 'Successfully logged out'} if success else False

        except Exception as e:
            logger.error(f"Error during logout: {e}")
            raise

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify a token and return user data.

        Args:
            token: JWT token

        Returns:
            User object or None if invalid

        Raises:
            ValueError: If token is blacklisted
        """
        try:
            # Check if blacklisted using token service
            if self.token_service.is_blacklisted(token):
                raise ValueError("Token blacklisted")

            token_data = self.token_service.validate_token(token)
            if not token_data:
                return None

            # Fetch fresh user data from repository
            user_dict = self.user_repo.get_by_id(token_data.user_id)

            if not user_dict or user_dict.get('is_deleted'):
                return None

            # Return User object for backward compatibility
            from app.schemas.user_schemas import User
            user_data = {k: v for k, v in user_dict.items() if k != 'password_hash'}
            return User(user_data)

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error verifying token: {e}")
            return None

    def change_password(
        self,
        user_id: int,
        current_password: str,
        new_password: str
    ) -> bool:
        """
        Change user password.

        Args:
            user_id: User ID
            current_password: Current password
            new_password: New password

        Returns:
            True if successful

        Raises:
            InvalidCredentialsException: If current password is wrong
            Exception: If user not found
        """
        try:
            # Fetch user with password hash from repository
            user_dict = self.user_repo.get_by_id(user_id)

            if not user_dict:
                raise Exception("User not found")

            # Verify current password
            if not self.password_service.verify_password(current_password, user_dict['password_hash']):
                raise Exception("Current password is incorrect")

            # Hash new password
            new_hash = self.password_service.hash_password(new_password)

            # Update password via repository
            success = self.user_repo.change_password(user_id, new_hash)

            if success:
                logger.info(f"Password changed for user ID: {user_id}")

            return success
        except Exception as e:
            logger.error(f"Error changing password: {e}")
            raise

    def refresh_token(self, old_token: str) -> Optional[TokenResponse]:
        """
        Refresh an access token.

        Args:
            old_token: Current token

        Returns:
            New TokenResponse or None if invalid
        """
        try:
            new_token = self.token_service.refresh_token(old_token)
            if not new_token:
                return None

            return TokenResponse(
                access_token=new_token,
                token_type="bearer",
                expires_in=3600
            )

        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            return None

    def get_current_user(self, token: str) -> Optional[UserResponse]:
        """
        Get current user from token.

        Args:
            token: JWT token

        Returns:
            UserResponse or None
        """
        try:
            user_data = self.verify_token(token)
            if not user_data:
                return None

            # Handle both dict and User object
            if hasattr(user_data, 'toJson'):
                user_dict = user_data.toJson()
            else:
                user_dict = user_data

            return UserResponse(**user_dict)

        except Exception as e:
            logger.error(f"Error getting current user: {e}")
            return None

    def is_admin(self, token: str) -> bool:
        """
        Check if token belongs to an admin user.

        Args:
            token: JWT token

        Returns:
            True if admin, False otherwise
        """
        return self.token_service.verify_admin(token)

    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Decode token without full verification (for debugging/logging).

        Args:
            token: JWT token to decode

        Returns:
            Decoded token data or None if malformed
        """
        try:
            # Delegate to token service
            return self.token_service.decode_token_payload(token)
        except Exception as e:
            logger.error(f"Error decoding token: {e}")
            return None
