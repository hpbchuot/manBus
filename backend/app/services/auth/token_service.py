"""
JWT token generation and validation service.
Handles token creation, validation, and blacklisting via repository pattern.
"""
import jwt
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from app.config.security import JWT_SECRET_KEY
from app.repositories.auth_repository import AuthRepository
from app.schemas.auth_schemas import TokenData

logger = logging.getLogger(__name__)


class TokenService:
    """
    Service for JWT token operations.
    Handles token generation, validation, and blacklist management.
    Uses AuthRepository for data access.
    """

    def __init__(self, auth_repository: AuthRepository, secret_key: str = None, algorithm: str = 'HS256'):
        """
        Initialize token service.

        Args:
            auth_repository: Auth repository for blacklist operations
            secret_key: Secret key for JWT encoding (default: from config)
            algorithm: JWT algorithm (default: HS256)
        """
        self.auth_repo = auth_repository
        self.secret_key = secret_key or JWT_SECRET_KEY
        self.algorithm = algorithm

    def generate_token(
        self,
        user_id: int,
        username: str,
        public_id: str,
        admin: bool = False,
        expires_in: int = 3600
    ) -> str:
        """
        Generate a JWT token for a user.

        Args:
            user_id: User's database ID
            username: Username
            public_id: User's public ID
            admin: Whether user is admin
            expires_in: Token expiration in seconds (default: 1 hour)

        Returns:
            Encoded JWT token string
        """
        try:
            # Get current time as Unix timestamp
            now = datetime.now()
            iat_timestamp = int(now.timestamp())
            exp_timestamp = int((now + timedelta(seconds=expires_in)).timestamp())

            # Create payload
            payload = {
                'user_id': user_id,
                'username': username,
                'public_id': public_id,
                'admin': admin,
                'exp': exp_timestamp,
                'iat': iat_timestamp
            }

            # Encode token
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

            logger.info(f"Generated token for user {username} (ID: {user_id})")
            return token

        except Exception as e:
            logger.error(f"Error generating token: {e}")
            raise

    def validate_token(self, token: str) -> Optional[TokenData]:
        """
        Validate and decode a JWT token.

        Args:
            token: JWT token string

        Returns:
            TokenData object if valid, None if invalid
        """
        try:
            # Check if token is blacklisted using repository
            if self.auth_repo.is_token_blacklisted(token):
                logger.warning("Attempted to use blacklisted token")
                return None

            # Decode and validate token
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )

            # Create TokenData from payload
            token_data = TokenData(
                user_id=payload.get('user_id'),
                username=payload.get('username'),
                public_id=payload.get('public_id'),
                admin=payload.get('admin', False),
                exp=payload.get('exp')
            )

            return token_data

        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
        except Exception as e:
            logger.error(f"Error validating token: {e}")
            return None

    def decode_token_without_validation(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Decode token without signature validation (for inspection).

        Args:
            token: JWT token string

        Returns:
            Decoded payload or None
        """
        try:
            payload = jwt.decode(
                token,
                options={"verify_signature": False}
            )
            return payload
        except Exception as e:
            logger.error(f"Error decoding token: {e}")
            return None

    def blacklist_token(self, token: str) -> bool:
        """
        Add a token to the blacklist using repository.

        Args:
            token: JWT token to blacklist

        Returns:
            True if successful (idempotent)
        """
        try:
            success = self.auth_repo.blacklist_token(token)

            if success:
                logger.info(f"Token blacklisted: {token[:20]}...")

            return success

        except Exception as e:
            logger.error(f"Error blacklisting token: {e}")
            raise

    def is_blacklisted(self, token: str) -> bool:
        """
        Check if a token is blacklisted using repository.

        Args:
            token: JWT token to check

        Returns:
            True if blacklisted, False otherwise
        """
        try:
            return self.auth_repo.is_token_blacklisted(token)

        except Exception as e:
            logger.error(f"Error checking blacklist: {e}")
            return False

    def cleanup_expired_blacklist(self, days_old: int = 30) -> int:
        """
        Remove old tokens from blacklist using repository.

        Args:
            days_old: Remove tokens older than this many days

        Returns:
            Number of tokens removed
        """
        try:
            count = self.auth_repo.cleanup_old_tokens(days_old)
            logger.info(f"Cleaned up {count} expired blacklist tokens")
            return count

        except Exception as e:
            logger.error(f"Error cleaning up blacklist: {e}")
            raise

    def get_token_expiration(self, token: str) -> Optional[datetime]:
        """
        Get expiration time from a token without full validation.

        Args:
            token: JWT token

        Returns:
            Expiration datetime or None
        """
        try:
            payload = self.decode_token_without_validation(token)
            if payload and 'exp' in payload:
                return datetime.fromtimestamp(payload['exp'])
            return None
        except Exception as e:
            logger.error(f"Error getting token expiration: {e}")
            return None

    def refresh_token(self, old_token: str, expires_in: int = 3600) -> Optional[str]:
        """
        Refresh a token by validating the old one and generating a new one.

        Args:
            old_token: Current valid token
            expires_in: New token expiration in seconds

        Returns:
            New token or None if old token is invalid
        """
        try:
            # Validate old token
            token_data = self.validate_token(old_token)
            if not token_data:
                return None

            # Blacklist old token
            self.blacklist_token(old_token)

            # Generate new token
            new_token = self.generate_token(
                user_id=token_data.user_id,
                username=token_data.username or '',
                public_id=token_data.public_id or '',
                admin=token_data.admin,
                expires_in=expires_in
            )

            logger.info(f"Token refreshed for user {token_data.username}")
            return new_token

        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            return None

    def extract_user_id(self, token: str) -> Optional[int]:
        """
        Extract user ID from token.

        Args:
            token: JWT token

        Returns:
            User ID or None
        """
        token_data = self.validate_token(token)
        return token_data.user_id if token_data else None

    def verify_admin(self, token: str) -> bool:
        """
        Verify if token belongs to an admin user.

        Args:
            token: JWT token

        Returns:
            True if admin, False otherwise
        """
        token_data = self.validate_token(token)
        return token_data.admin if token_data else False


# Backward compatibility - standalone functions
def generate_token(user_id: int, username: str, public_id: str, admin: bool = False) -> str:
    """Generate token (backward compatible)"""
    from app.config.database import Database
    from app.repositories.auth_repository import AuthRepository
    db = Database()
    auth_repo = AuthRepository(db)
    service = TokenService(auth_repo)
    return service.generate_token(user_id, username, public_id, admin)


def validate_token(token: str) -> Optional[Dict[str, Any]]:
    """Validate token (backward compatible)"""
    from app.config.database import Database
    from app.repositories.auth_repository import AuthRepository
    db = Database()
    auth_repo = AuthRepository(db)
    service = TokenService(auth_repo)
    token_data = service.validate_token(token)
    if token_data:
        return {
            'user_id': token_data.user_id,
            'username': token_data.username,
            'public_id': token_data.public_id,
            'admin': token_data.admin
        }
    return None
