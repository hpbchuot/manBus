from app.core.interfaces.services.blacklist_service_interface import IBlacklistService

class BlacklistService:
    """Token blacklist service using database functions"""

    def __init__(self, db_executor):
        """
        Initialize blacklist service

        Args:
            db_executor: Database connection for queries
        """
        self._db = db_executor

    def is_blacklisted(self, token):
        """Check if token is blacklisted using fn_is_token_blacklisted"""
        result = self._db.fetch_one(
            "SELECT fn_is_token_blacklisted(%s) AS is_blacklisted",
            (token,)
        )
        return result['is_blacklisted'] if result else False

    def add_to_blacklist(self, token):
        """Add token to blacklist using fn_blacklist_token"""
        self._db.execute_query(
            "SELECT fn_blacklist_token(%s)",
            (token,)
        )
        return True

    def remove_from_blacklist(self, token):
        """Remove token from blacklist"""
        self._db.execute_query(
            "DELETE FROM BlacklistTokens WHERE token = %s",
            (token,)
        )
        return True

    def cleanup_old_tokens(self, days_old=30):
        """
        Remove old tokens from blacklist using fn_cleanup_old_tokens

        Args:
            days_old: Number of days after which tokens should be removed (default: 30)

        Returns:
            int: Number of tokens deleted
        """
        result = self._db.fetch_one(
            "SELECT fn_cleanup_old_tokens(%s) AS deleted_count",
            (days_old,)
        )
        return result['deleted_count'] if result else 0
