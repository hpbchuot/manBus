"""Role service interface following Interface Segregation Principle"""
from abc import ABC, abstractmethod


class IRoleService(ABC):
    """Interface for role management operations"""

    @abstractmethod
    def user_has_role(self, user_id, role_name):
        """
        Check if a user has a specific role

        Args:
            user_id: User ID to check
            role_name: Name of the role to check for

        Returns:
            bool: True if user has the role, False otherwise
        """
        pass

    @abstractmethod
    def assign_role(self, user_id, role_name):
        """
        Assign a role to a user

        Args:
            user_id: User ID to assign role to
            role_name: Name of the role to assign

        Returns:
            bool: True if successful, False if role already assigned
        """
        pass

    @abstractmethod
    def revoke_role(self, user_id, role_name):
        """
        Revoke a role from a user

        Args:
            user_id: User ID to revoke role from
            role_name: Name of the role to revoke

        Returns:
            bool: True if successful, False if user didn't have the role
        """
        pass

    @abstractmethod
    def get_user_roles(self, user_id):
        """
        Get all roles assigned to a user

        Args:
            user_id: User ID to get roles for

        Returns:
            list: List of role dictionaries
        """
        pass

    @abstractmethod
    def get_users_by_role(self, role_name):
        """
        Get all users with a specific role

        Args:
            role_name: Name of the role

        Returns:
            list: List of user dictionaries
        """
        pass
