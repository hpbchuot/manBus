from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from app.schemas.user_schemas import UserCreate, UserResponse

class IRegistrationService(ABC):
    """
    Interface for user registration.
    Single Responsibility: User registration only.
    Follows ISP - clients that only need registration don't depend on login/logout methods.
    """

    @abstractmethod
    def register(self, user_data: UserCreate) -> Optional[UserResponse]:
        """
        Register a new user.

        Args:
            user_data: User registration data

        Returns:
            UserResponse or None if registration failed

        Raises:
            ValueError: If validation fails or user already exists
        """
        pass


class IAuthenticationService(ABC):
    """
    Interface for user authentication (login/logout).
    Single Responsibility: Authentication only.
    Follows ISP - clients that only need authentication don't depend on registration/verification.
    """

    @abstractmethod
    def login(self, credentials):
        """
        Authenticate user and return token.

        Args:
            credentials: Login credentials (username/email and password)

        Returns:
            LoginResponse with access and refresh tokens

        Raises:
            ValueError: If authentication fails
        """
        pass

    @abstractmethod
    def logout(self, token: str) -> bool:
        """
        Invalidate token (add to blacklist).

        Args:
            token: Access token to invalidate

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def refresh_token(self, refresh_token: str):
        """
        Refresh access token using refresh token.

        Args:
            refresh_token: Refresh token

        Returns:
            LoginResponse with new access token

        Raises:
            ValueError: If refresh token is invalid or expired
        """
        pass


class ITokenVerificationService(ABC):
    """
    Interface for token verification.
    Single Responsibility: Token verification and decoding only.
    Follows ISP - clients that only need token verification don't depend on login/registration.
    """

    @abstractmethod
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify token validity and return decoded data.

        Args:
            token: JWT token to verify

        Returns:
            Decoded token data or None if invalid

        Raises:
            ValueError: If token is invalid, expired, or blacklisted
        """
        pass

    @abstractmethod
    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Decode token without full verification (for debugging/logging).

        Args:
            token: JWT token to decode

        Returns:
            Decoded token data or None if malformed
        """
        pass


class IAuthService(IRegistrationService, IAuthenticationService, ITokenVerificationService):
    """
    Composite interface combining all auth operations.
    Clients can depend on specific interfaces (IRegistrationService, IAuthenticationService, etc.)
    instead of this broad interface.

    This follows ISP by allowing clients to depend only on the methods they need:
    - Controllers that only handle registration: depend on IRegistrationService
    - Controllers that only handle login: depend on IAuthenticationService
    - Middleware that verifies tokens: depend on ITokenVerificationService
    - Full auth service: implement this composite interface
    """
    pass
