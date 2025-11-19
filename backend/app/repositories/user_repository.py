"""
User Repository - Data access layer for user operations
Calls PostgreSQL functions and returns RealDictRow results
"""
from typing import Optional, List, Dict, Any
from .base_repository import BaseRepository


class UserRepository(BaseRepository):
    """
    User repository - handles all user data access via PostgreSQL functions.
    Returns RealDictRow objects (dict-like) from database.
    """

    def _get_table_name(self):
        return 'users'

    def _get_id_column(self):
        return 'id'

    def create(self, entity: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a new user using fn_create_user function.

        Args:
            entity: Dict with name, phone, email, username, password_hash, public_id, admin

        Returns:
            RealDictRow with created user data or None
        """
        query = '''
            SELECT fn_create_user(%s, %s, %s, %s, %s) AS result
        '''
        params = (
            entity.get('name'),
            entity.get('phone'),
            entity.get('email'),
            entity.get('username'),
            entity.get('password')
        )
        result = self._db.fetch_one(query, params)
        return self.get_by_id(result['result'])

    def update(self, user_id: int, entity: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update user using fn_update_user function.

        Args:
            user_id: User ID
            entity: Dict with fields to update (name, phone, email, username)

        Returns:
            RealDictRow with updated user data or None
        """
        query = '''
            SELECT * FROM fn_update_user(%s, %s, %s, %s, %s)
        '''
        params = (
            user_id,
            entity.get('name'),
            entity.get('phone'),
            entity.get('email'),
            entity.get('username')
        )
        result = self._db.fetch_one(query, params)
        return dict(result) if result else None

    def get_by_id(self, user_id: int):
        """
        Get user by ID using fn_get_user_by_id function.

        Args:
            user_id: User ID

        Returns:
            RealDictRow with user data or None
        """
        query = 'SELECT * FROM fn_get_user_by_id(%s)'
        result = self._db.fetch_one(query, (user_id,))
        return result

    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get user by email using fn_get_user_by_email function.

        Args:
            email: User email

        Returns:
            RealDictRow with user data or None
        """
        query = 'SELECT * FROM fn_get_user_by_email(%s)'
        result = self._db.fetch_one(query, (email,))
        return dict(result) if result else None

    def get_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get user by username using fn_get_user_by_username function.

        Args:
            username: Username

        Returns:
            RealDictRow with user data or None
        """
        query = 'SELECT * FROM fn_get_user_by_username(%s)'
        result = self._db.fetch_one(query, (username,))
        return dict(result) if result else None

    def get_by_public_id(self, public_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user by public_id using fn_get_user_by_public_id function.

        Args:
            public_id: User UUID

        Returns:
            RealDictRow with user data or None
        """
        query = 'SELECT * FROM fn_get_user_by_public_id(%s)'
        result = self._db.fetch_one(query, (public_id,))
        return dict(result) if result else None

    def get_by_username_or_email(self, identifier: str) -> Optional[Dict[str, Any]]:
        """
        Get user by username or email (for login) using fn_get_user_by_username_or_email.

        Args:
            identifier: Username or email

        Returns:
            RealDictRow with user data or None
        """
        query = 'SELECT * FROM fn_get_user_by_username_or_email(%s)'
        result = self._db.fetch_one(query, (identifier,))
        return dict(result) if result else None

    def soft_delete(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Soft delete user using fn_soft_delete_user function.

        Args:
            user_id: User ID

        Returns:
            RealDictRow with deleted user data or None
        """
        query = 'SELECT * FROM fn_soft_delete_user(%s)'
        result = self._db.fetch_one(query, (user_id,))
        return dict(result) if result else None

    def restore(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Restore soft-deleted user using fn_restore_user function.

        Args:
            user_id: User ID

        Returns:
            RealDictRow with restored user data or None
        """
        query = 'SELECT * FROM fn_restore_user(%s)'
        result = self._db.fetch_one(query, (user_id,))
        return dict(result) if result else None

    def search(
        self,
        query: Optional[str] = None,
        admin_only: Optional[bool] = None,
        include_deleted: bool = False,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Search users using fn_search_users function.

        Args:
            query: Search term for name, email, username
            admin_only: Filter admin users only
            include_deleted: Include soft-deleted users
            limit: Max results
            offset: Offset for pagination

        Returns:
            List of RealDictRow with user data
        """
        sql = 'SELECT * FROM fn_search_users(%s, %s, %s, %s, %s)'
        results = self._db.fetch_all(sql, (query, admin_only, include_deleted, limit, offset))
        return [dict(row) for row in results] if results else []

    def get_all(
        self,
        include_deleted: bool = False,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get all users using fn_get_all_users function.

        Args:
            include_deleted: Include soft-deleted users
            limit: Max results
            offset: Offset for pagination

        Returns:
            List of RealDictRow with user data
        """
        query = 'SELECT * FROM fn_get_all_users(%s, %s, %s)'
        results = self._db.fetch_all(query, (include_deleted, limit, offset))
        return [dict(row) for row in results] if results else []

    def count(
        self,
        query: Optional[str] = None,
        admin_only: Optional[bool] = None,
        include_deleted: bool = False
    ) -> int:
        """
        Count users using fn_count_users function.

        Args:
            query: Search term
            admin_only: Filter admin users only
            include_deleted: Include soft-deleted users

        Returns:
            Count of matching users
        """
        sql = 'SELECT fn_count_users(%s, %s, %s) AS count'
        result = self._db.fetch_one(sql, (query, admin_only, include_deleted))
        return result['count'] if result else 0

    def get_with_roles(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user with roles using fn_get_user_with_roles function.

        Args:
            user_id: User ID

        Returns:
            RealDictRow with user data and roles array or None
        """
        query = 'SELECT * FROM fn_get_user_with_roles(%s)'
        result = self._db.fetch_one(query, (user_id,))
        return dict(result) if result else None

    def user_exists(self, email: str, username: str) -> bool:
        """
        Check if user exists by email or username using fn_user_exists function.

        Args:
            email: Email to check
            username: Username to check

        Returns:
            True if user exists, False otherwise
        """
        query = 'SELECT * FROM users where email = %s OR username = %s'
        result = self._db.fetch_one(query, (email, username))
        return True if result else False

    def change_password(self, user_id: int, new_password_hash: str) -> bool:
        """
        Change user password using fn_change_user_password function.

        Args:
            user_id: User ID
            new_password_hash: New bcrypt password hash

        Returns:
            True if successful, False otherwise
        """
        query = 'SELECT fn_change_user_password(%s, %s) AS success'
        result = self._db.fetch_one(query, (user_id, new_password_hash))
        return result['success'] if result else False

    def assign_role(self, user_id: int, role_id: int) -> bool:
        """
        Assign role to user using fn_assign_user_role function.

        Args:
            user_id: User ID
            role_id: Role ID

        Returns:
            True if successful (idempotent)
        """
        query = 'SELECT fn_assign_user_role(%s, %s) AS success'
        result = self._db.fetch_one(query, (user_id, role_id))
        return result['success'] if result else False

    def remove_role(self, user_id: int, role_id: int) -> bool:
        """
        Remove role from user using fn_remove_user_role function.

        Args:
            user_id: User ID
            role_id: Role ID

        Returns:
            True if successful, False if not found
        """
        query = 'SELECT fn_remove_user_role(%s, %s) AS success'
        result = self._db.fetch_one(query, (user_id, role_id))
        return result['success'] if result else False

    def has_role(self, user_id: int, role_name: str) -> bool:
        """
        Check if user has specific role using fn_user_has_role function.

        Args:
            user_id: User ID
            role_name: Role name to check

        Returns:
            True if user has role, False otherwise
        """
        query = 'SELECT fn_user_has_role(%s, %s) AS has_role'
        result = self._db.fetch_one(query, (user_id, role_name))
        return result['has_role'] if result else False

    def get_roles(self, user_id: int) -> List[str]:
        """
        Get all roles for user using fn_get_user_roles function.

        Args:
            user_id: User ID

        Returns:
            List of role names
        """
        query = 'SELECT fn_get_user_roles(%s) AS roles'
        result = self._db.fetch_one(query, (user_id,))
        return result['roles'] if result and result['roles'] else []