"""
Password hashing and verification service.
Handles secure password operations using bcrypt.
"""
import bcrypt
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class PasswordService:
    """
    Service for password hashing and verification.
    Uses bcrypt for secure password hashing.
    """

    @staticmethod
    def hash_password(password: str, rounds: int = 12) -> str:
        """
        Hash a password using bcrypt.

        Args:
            password: Plain text password
            rounds: Number of bcrypt rounds (default: 12)

        Returns:
            Hashed password string

        Raises:
            ValueError: If password is empty or invalid
        """
        if not password:
            raise ValueError("Password cannot be empty")

        if len(password) > 72:
            raise ValueError("Password too long (max 72 characters)")

        try:
            # Generate salt and hash password
            salt = bcrypt.gensalt(rounds=rounds)
            password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)

            # Return as string (decoded)
            return password_hash.decode('utf-8')

        except Exception as e:
            logger.error(f"Error hashing password: {e}")
            raise

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """
        Verify a password against its hash.

        Args:
            password: Plain text password to verify
            password_hash: Hashed password to compare against

        Returns:
            True if password matches, False otherwise
        """
        if not password or not password_hash:
            return False

        try:
            # Compare password with hash
            return bcrypt.checkpw(
                password.encode('utf-8'),
                password_hash.encode('utf-8')
            )

        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False

    @staticmethod
    def needs_rehash(password_hash: str, rounds: int = 12) -> bool:
        """
        Check if a password hash needs to be rehashed with more rounds.

        Args:
            password_hash: Existing password hash
            rounds: Desired number of rounds

        Returns:
            True if rehash is needed
        """
        try:
            # Extract the rounds from the hash
            # bcrypt hash format: $2b$rounds$salthash
            parts = password_hash.split('$')
            if len(parts) >= 3:
                current_rounds = int(parts[2])
                return current_rounds < rounds
            return False

        except Exception as e:
            logger.error(f"Error checking rehash requirement: {e}")
            return False

    @classmethod
    def validate_password_strength(cls, password: str) -> tuple[bool, Optional[str]]:
        """
        Validate password strength requirements.

        Args:
            password: Password to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not password:
            return False, "Password cannot be empty"

        if len(password) < 8:
            return False, "Password must be at least 8 characters long"

        if len(password) > 72:
            return False, "Password too long (max 72 characters)"

        # Check for uppercase letter
        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"

        # Check for lowercase letter
        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"

        # Check for digit
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one digit"

        return True, None

    @classmethod
    def generate_secure_password(cls, length: int = 16) -> str:
        """
        Generate a secure random password.

        Args:
            length: Desired password length (default: 16)

        Returns:
            Randomly generated secure password
        """
        import secrets
        import string

        if length < 8:
            length = 8

        # Character sets
        uppercase = string.ascii_uppercase
        lowercase = string.ascii_lowercase
        digits = string.digits
        special = "!@#$%^&*()-_=+[]{}|;:,.<>?"

        # Ensure at least one of each required type
        password = [
            secrets.choice(uppercase),
            secrets.choice(lowercase),
            secrets.choice(digits),
            secrets.choice(special)
        ]

        # Fill the rest randomly
        all_chars = uppercase + lowercase + digits + special
        for _ in range(length - 4):
            password.append(secrets.choice(all_chars))

        # Shuffle the password
        secrets.SystemRandom().shuffle(password)

        return ''.join(password)


# Backward compatibility - standalone functions
def hash_password(password: str) -> str:
    """Hash a password (backward compatible)"""
    return PasswordService.hash_password(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password (backward compatible)"""
    return PasswordService.verify_password(password, password_hash)
