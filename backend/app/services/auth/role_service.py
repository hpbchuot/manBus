"""Role service implementation using database functions"""
from app.core.interfaces.services.role_service_interface import IRoleService


class RoleService(IRoleService):
    """Role management service using database functions"""

    def __init__(self, db_executor):
        """
        Initialize role service

        Args:
            db_executor: Database connection for queries
        """
        self._db = db_executor

    def user_has_role(self, user_id, role_name):
        """Check if a user has a specific role using fn_user_has_role"""
        result = self._db.fetch_one(
            "SELECT fn_user_has_role(%s, %s) AS has_role",
            (user_id, role_name)
        )
        return result['has_role'] if result else False

    def assign_role(self, user_id, role_name):
        """Assign a role to a user using fn_assign_role"""
        result = self._db.fetch_one(
            "SELECT fn_assign_role(%s, %s) AS success",
            (user_id, role_name)
        )
        return result['success'] if result else False

    def revoke_role(self, user_id, role_name):
        """Revoke a role from a user using fn_revoke_role"""
        result = self._db.fetch_one(
            "SELECT fn_revoke_role(%s, %s) AS success",
            (user_id, role_name)
        )
        return result['success'] if result else False

    def get_user_roles(self, user_id):
        """Get all roles assigned to a user using fn_get_user_roles"""
        result = self._db.fetch_all(
            "SELECT * FROM fn_get_user_roles(%s)",
            (user_id,)
        )
        return [dict(row) for row in result] if result else []

    def get_users_by_role(self, role_name):
        """Get all users with a specific role using fn_get_users_by_role"""
        result = self._db.fetch_all(
            "SELECT * FROM fn_get_users_by_role(%s)",
            (role_name,)
        )
        return [dict(row) for row in result] if result else []
