"""
User service for managing user operations with repository pattern.
Uses: Repository → Service → Schema → Controller

Architecture (SRP Compliance):
- UserCrudService: Core CRUD operations (create, get, update, delete)
- UserSearchService: Search and filtering operations
- UserLookupService: User lookup by email, username, public_id
- UserRoleService: Role management operations
- UserPasswordService: Password management operations
- UserService: Facade/Composite that delegates to all specialized services
"""
import logging
from typing import Any, Optional, List, Dict

from app.repositories.user_repository import UserRepository
from app.schemas.user_schemas import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserDetailResponse,
    UserWithRoles,
    UserSearchParams,
    UserPasswordUpdate
)
from app.schemas.base_schema import PaginationParams, PaginatedResponse

logger = logging.getLogger(__name__)


class UserCrudService:
    """
    User CRUD service - handles core Create, Read, Update, Delete operations.
    Single Responsibility: Basic user lifecycle management.
    """

    def __init__(self, user_repository: UserRepository):
        """Initialize with dependencies."""
        self.user_repo = user_repository

    def create_user(self, user_data: UserCreate) -> UserResponse:
        """
        Create a new user.

        Args:
            user_data: UserCreate schema with user data

        Returns:
            UserResponse with created user data

        Raises:
            ValueError: If user already exists
        """
        try:
            # Check if user exists using repository
            if self.user_repo.user_exists(user_data.email, user_data.username):
                raise ValueError("User with this email or username already exists")

            # Prepare entity for repository
            entity = {
                'name': user_data.name,
                'phone': user_data.phone,
                'email': user_data.email,
                'username': user_data.username,
                'password': user_data.password
            }

            # Create user via repository
            user_dict = self.user_repo.create(entity)

            if not user_dict:
                raise Exception("Failed to create user")

            # Remove password_hash and convert to schema
            user_data_clean = {k: v for k, v in user_dict.items() if k != 'password_hash'}

            logger.info(f"User created: {user_data.username} (ID: {user_dict['id']})")
            return UserResponse(**user_data_clean)

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise

    def get_user(self, user_id: int) -> Optional[UserResponse]:
        """
        Get user by ID.

        Args:
            user_id: User ID

        Returns:
            UserResponse or None if not found
        """
        try:
            user_dict = self.user_repo.get_by_id(user_id)
            if not user_dict:
                return None

            # Remove password_hash and convert to schema
            user_data = {k: v for k, v in user_dict.items() if k != 'password_hash'}
            return UserResponse(**user_data)

        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            raise

    def get_user_detail(self, user_id: int) -> Optional[UserDetailResponse]:
        """
        Get detailed user information including soft-delete status.

        Args:
            user_id: User ID

        Returns:
            UserDetailResponse or None
        """
        try:
            user_dict = self.user_repo.get_by_id(user_id)
            if not user_dict:
                return None

            user_data = {k: v for k, v in user_dict.items() if k != 'password_hash'}
            return UserDetailResponse(**user_data)

        except Exception as e:
            logger.error(f"Error getting user detail {user_id}: {e}")
            raise

    def update_user(self, user_id: int, user_data: UserUpdate) -> bool:
        """
        Update user information.

        Args:
            user_id: User ID
            user_data: UserUpdate schema with update data

        Returns:
            Updated UserResponse or None if not found
        """
        try:
            # Build update entity (exclude None values)
            update_entity = user_data.model_dump(exclude_none=True)

            if not update_entity:
                # No updates provided, return current user
                return self.get_user(user_id)

            # Check for email/username conflicts if being updated
            if 'email' in update_entity or 'username' in update_entity:
                current_user = self.user_repo.get_by_id(user_id)
                if not current_user:
                    return None

                # Check if new email conflicts with another user
                if 'email' in update_entity and update_entity['email'] != current_user.get('email'):
                    existing = self.user_repo.get_by_email(update_entity['email'])
                    if existing and existing['id'] != user_id:
                        raise ValueError("Email already in use by another user")

                # Check if new username conflicts with another user
                if 'username' in update_entity and update_entity['username'] != current_user.get('username'):
                    existing = self.user_repo.get_by_username(update_entity['username'])
                    if existing and existing['id'] != user_id:
                        raise ValueError("Username already in use by another user")

            # Update user via repository
            result_dict = self.user_repo.update(user_id, update_entity)
            return result_dict['fn_update_user_profile']

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            raise

    def delete_user(self, user_id: int, hard_delete: bool = False) -> bool:
        """
        Delete user (soft or hard delete).

        Args:
            user_id: User ID
            hard_delete: If True, permanently delete. If False, soft delete.

        Returns:
            True if successful
        """
        try:
            if hard_delete:
                # Hard delete not implemented in repository - would need SQL function
                raise NotImplementedError("Hard delete not implemented via repository pattern")
            else:
                result = self.user_repo.soft_delete(user_id)
                return result is not None

        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {e}")
            raise

    def restore_user(self, user_id: int) -> bool:
        """
        Restore a soft-deleted user.

        Args:
            user_id: User ID

        Returns:
            Restored UserResponse or None
        """
        try:
            user_dict = self.user_repo.restore(user_id)
            if not user_dict:
                return False
            
            return True

        except Exception as e:
            logger.error(f"Error restoring user {user_id}: {e}")
            raise


class UserSearchService:
    """
    User search service - handles searching, filtering, and listing users.
    Single Responsibility: User search and retrieval operations.
    """

    def __init__(self, user_repository: UserRepository):
        """Initialize with user repository."""
        self.user_repo = user_repository

    def search_users(
        self,
        query: str
    ) -> List[Dict[str, Any]]:
        """
        Search users with filters.

        Args:
            search_params: Search parameters

        Returns:
            List of UserResponse
        """
        try:
            # Perform search via repository
            user_dicts = self.user_repo.search(query)
            return user_dicts
        except Exception as e:
            logger.error(f"Error searching users: {e}")
            raise

    def get_all_users(
        self,
        cursor: Optional[int] = None,
        limit: Optional[int] = None,
        role: Optional[str] = None,
        include_deleted: bool = False,
    ) -> List[UserResponse]:
        """
        Get all users with cursor-based pagination.

        Args:
            cursor: Optional cursor for pagination (user ID from last result)
            limit: Optional limit for number of users (default 20, max 100)
            role: Optional role to filter users
            include_deleted: Whether to include soft-deleted users

        Returns:
            List of UserResponse (use last item's ID as cursor for next page)
        """
        try:
            user_dicts = self.user_repo.get_all(cursor, limit, role, include_deleted)

            users = []
            for user_dict in user_dicts:
                user_data = {k: v for k, v in user_dict.items() if k != 'password_hash'}
                users.append(UserResponse(**user_data))

            return users

        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            raise


class UserLookupService:
    """
    User lookup service - handles finding users by various identifiers.
    Single Responsibility: User lookup by email, username, public_id.
    """

    def __init__(self, user_repository: UserRepository):
        """Initialize with user repository."""
        self.user_repo = user_repository

    def get_by_email(self, email: str) -> Optional[UserResponse]:
        """
        Get user by email address.

        Args:
            email: Email address

        Returns:
            UserResponse or None
        """
        try:
            user_dict = self.user_repo.get_by_email(email)
            if not user_dict:
                return None

            user_data = {k: v for k, v in user_dict.items() if k != 'password_hash'}
            return UserResponse(**user_data)

        except Exception as e:
            logger.error(f"Error getting user by email {email}: {e}")
            raise

    def get_by_username(self, username: str) -> Optional[UserResponse]:
        """
        Get user by username.

        Args:
            username: Username

        Returns:
            UserResponse or None
        """
        try:
            user_dict = self.user_repo.get_by_username(username)
            if not user_dict:
                return None

            user_data = {k: v for k, v in user_dict.items() if k != 'password_hash'}
            return UserResponse(**user_data)

        except Exception as e:
            logger.error(f"Error getting user by username {username}: {e}")
            raise

    def get_by_public_id(self, public_id: str) -> Optional[UserResponse]:
        """
        Get user by public ID.

        Args:
            public_id: Public ID

        Returns:
            UserResponse or None
        """
        try:
            user_dict = self.user_repo.get_by_public_id(public_id)
            if not user_dict:
                return None

            user_data = {k: v for k, v in user_dict.items() if k != 'password_hash'}
            return UserResponse(**user_data)

        except Exception as e:
            logger.error(f"Error getting user by public_id: {e}")
            raise


class UserRoleService:
    """
    User role service - handles role assignment and management.
    Single Responsibility: User role operations.
    """

    def __init__(self, user_repository: UserRepository):
        """Initialize with user repository."""
        self.user_repo = user_repository

    def assign_role(self, user_id: int, role_id: int) -> bool:
        """
        Assign a role to a user.

        Args:
            user_id: User ID
            role_id: Role ID

        Returns:
            True if successful (idempotent)
        """
        try:
            success = self.user_repo.assign_role(user_id, role_id)

            if success:
                logger.info(f"Role {role_id} assigned to user {user_id}")

            return success

        except Exception as e:
            logger.error(f"Error assigning role: {e}")
            raise

    def remove_role(self, user_id: int, role_id: int) -> bool:
        """
        Remove a role from a user.

        Args:
            user_id: User ID
            role_id: Role ID

        Returns:
            True if successful, False if not found
        """
        try:
            success = self.user_repo.remove_role(user_id, role_id)

            if success:
                logger.info(f"Role {role_id} removed from user {user_id}")

            return success

        except Exception as e:
            logger.error(f"Error removing role: {e}")
            raise


class UserService:
    """
    Composite User Service - Facade pattern for all user operations.

    Aggregates specialized services following SRP:
    - UserCrudService: CRUD operations
    - UserSearchService: Search & filtering
    - UserLookupService: User lookup
    - UserRoleService: Role management
    - UserPasswordService: Password management

    This class delegates to specialized services while providing
    a single, unified interface for the controller layer.
    """

    def __init__(self, user_repository: UserRepository):
        """
        Initialize composite user service.

        Args:
            user_repository: User repository for data access
        """
        # Initialize specialized services
        self._crud = UserCrudService(user_repository)
        self._search = UserSearchService(user_repository)
        self._lookup = UserLookupService(user_repository)
        self._roles = UserRoleService(user_repository)

        # Keep references for backward compatibility
        self.user_repo = user_repository
    # === CRUD Operations (delegate to UserCrudService) ===
    def create_user(self, user_data: UserCreate) -> UserResponse:
        return self._crud.create_user(user_data)

    def get_user(self, user_id: int) -> Optional[UserResponse]:
        return self._crud.get_user(user_id)

    def get_user_detail(self, user_id: int) -> Optional[UserDetailResponse]:
        return self._crud.get_user_detail(user_id)

    def update_user(self, user_id: int, user_data: UserUpdate) -> bool:
        return self._crud.update_user(user_id, user_data)

    def delete_user(self, user_id: int, hard_delete: bool = False) -> bool:
        return self._crud.delete_user(user_id, hard_delete)

    def restore_user(self, user_id: int) -> bool:
        return self._crud.restore_user(user_id)

    # === Search Operations (delegate to UserSearchService) ===
    def search_users(
        self,
        query: str
    ) -> List[Dict[str, Any]]:
        return self._search.search_users(query)

    def get_all_users(
        self,
        cursor: Optional[int] = None,
        limit: Optional[int] = None,
        role: Optional[str] = None,
        include_deleted: bool = False,
    ) -> List[UserResponse]:
        return self._search.get_all_users(cursor, limit, role, include_deleted)

    # === Lookup Operations (delegate to UserLookupService) ===
    def get_by_email(self, email: str) -> Optional[UserResponse]:
        return self._lookup.get_by_email(email)

    def get_by_username(self, username: str) -> Optional[UserResponse]:
        return self._lookup.get_by_username(username)

    def get_by_public_id(self, public_id: str) -> Optional[UserResponse]:
        return self._lookup.get_by_public_id(public_id)

    # === Role Operations (delegate to UserRoleService) ===

    def assign_role(self, user_id: int, role_id: int) -> bool:
        return self._roles.assign_role(user_id, role_id)

    def remove_role(self, user_id: int, role_id: int) -> bool:
        return self._roles.remove_role(user_id, role_id)

