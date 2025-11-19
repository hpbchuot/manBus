"""
Auth Repository - Data access layer for authentication operations
Handles token blacklist operations via PostgreSQL functions
"""
from typing import Optional, Dict, Any


class AuthRepository:
    """
    Auth repository - handles token blacklist data access via PostgreSQL functions.
    Returns RealDictRow objects (dict-like) from database.
    """

    def __init__(self, db_executor):
        """
        Initialize auth repository.

        Args:
            db_executor: Database instance (Database class)
        """
        self._db = db_executor

    def blacklist_token(self, token: str) -> bool:
        """
        Add token to blacklist using fn_blacklist_token function.

        Args:
            token: JWT token to blacklist

        Returns:
            True if successful (idempotent)
        """
        query = 'SELECT fn_blacklist_token(%s) AS success'
        result = self._db.fetch_one(query, (token,))
        return result['success'] if result else False

    def is_token_blacklisted(self, token: str) -> bool:
        """
        Check if token is blacklisted using fn_is_token_blacklisted function.

        Args:
            token: JWT token to check

        Returns:
            True if blacklisted, False otherwise
        """
        query = 'SELECT fn_is_token_blacklisted(%s) AS is_blacklisted'
        result = self._db.fetch_one(query, (token,))
        return result['is_blacklisted'] if result else False

    def cleanup_old_tokens(self, days_old: int = 30) -> int:
        """
        Remove old blacklisted tokens using fn_cleanup_old_blacklist_tokens function.

        Args:
            days_old: Remove tokens older than this many days

        Returns:
            Number of tokens removed
        """
        query = 'SELECT fn_cleanup_old_blacklist_tokens(%s) AS deleted_count'
        result = self._db.fetch_one(query, (days_old,))
        return result['deleted_count'] if result else 0

    def get_blacklist_stats(self) -> Optional[Dict[str, Any]]:
        """
        Get blacklist statistics using fn_get_blacklist_stats function.

        Returns:
            Dict with total_tokens, oldest_token_date, newest_token_date or None
        """
        query = 'SELECT * FROM fn_get_blacklist_stats()'
        result = self._db.fetch_one(query, None)
        return dict(result) if result else None

    def remove_token_from_blacklist(self, token: str) -> bool:
        """
        Remove specific token from blacklist using fn_remove_token_from_blacklist function.

        Args:
            token: JWT token to remove

        Returns:
            True if removed, False if not found
        """
        query = 'SELECT fn_remove_token_from_blacklist(%s) AS success'
        result = self._db.fetch_one(query, (token,))
        return result['success'] if result else False
    
    def verify_user_password(self, email: str, password: str) -> bool:
        """
        Verify user's password using fn_verify_user_password function.

        Args:
            email: Email of the user
            password: Password to verify

        Returns:
            True if password matches, False otherwise
        """
        query = 'SELECT fn_verify_user_password(%s, %s) AS userid'
        result = self._db.fetch_one(query, (email, password))
        return result['userid'] if result else False