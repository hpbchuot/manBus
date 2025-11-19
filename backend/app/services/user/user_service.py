"""
User service for managing user operations with repository pattern.
Uses: Repository → Service → Schema → Controller
"""
import logging
import uuid
from typing import Optional, List

from app.repositories.user_repository import UserRepository
from app.services.auth.password_service import PasswordService
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


class UserService:
    """
    User service handling all user-related operations.
    Uses UserRepository for data access, returns Pydantic schemas.
    """

    def __init__(self, user_repository: UserRepository, password_service: PasswordService):
        """
        Initialize user service.

        Args:
            user_repository: User repository for data access
            password_service: Password hashing service
        """
        self.user_repo = user_repository
        self.password_service = password_service

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

            # Hash password
            password_hash = self.password_service.hash_password(user_data.password)

            # Generate public_id
            public_id = str(uuid.uuid4())

            # Prepare entity for repository
            entity = {
                'name': user_data.name,
                'phone': user_data.phone,
                'email': user_data.email,
                'username': user_data.username,
                'password_hash': password_hash,
                'public_id': public_id,
                'admin': user_data.admin
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

    def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[UserResponse]:
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
            user_dict = self.user_repo.update(user_id, update_entity)

            if not user_dict:
                return None

            user_data_clean = {k: v for k, v in user_dict.items() if k != 'password_hash'}
            logger.info(f"User updated: ID {user_id}")
            return UserResponse(**user_data_clean)

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

    def restore_user(self, user_id: int) -> Optional[UserResponse]:
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
                return None

            user_data = {k: v for k, v in user_dict.items() if k != 'password_hash'}
            logger.info(f"User restored: ID {user_id}")
            return UserResponse(**user_data)

        except Exception as e:
            logger.error(f"Error restoring user {user_id}: {e}")
            raise

    def search_users(
        self,
        search_params: UserSearchParams,
        pagination: Optional[PaginationParams] = None
    ) -> List[UserResponse] | PaginatedResponse:
        """
        Search users with filters.

        Args:
            search_params: Search parameters
            pagination: Optional pagination params

        Returns:
            List of UserResponse or PaginatedResponse if paginated
        """
        try:
            if pagination:
                # Get total count via repository
                total = self.user_repo.count(
                    query=search_params.query,
                    admin_only=search_params.admin_only,
                    include_deleted=search_params.include_deleted
                )

                # Get paginated items via repository
                user_dicts = self.user_repo.search(
                    query=search_params.query,
                    admin_only=search_params.admin_only,
                    include_deleted=search_params.include_deleted,
                    limit=pagination.limit,
                    offset=pagination.offset
                )

                # Convert to schemas
                items = []
                for user_dict in user_dicts:
                    user_data = {k: v for k, v in user_dict.items() if k != 'password_hash'}
                    items.append(UserResponse(**user_data))

                return PaginatedResponse[UserResponse].create(
                    items=items,
                    total=total,
                    page=pagination.page,
                    page_size=pagination.page_size
                )
            else:
                # No pagination
                user_dicts = self.user_repo.search(
                    query=search_params.query,
                    admin_only=search_params.admin_only,
                    include_deleted=search_params.include_deleted
                )

                users = []
                for user_dict in user_dicts:
                    user_data = {k: v for k, v in user_dict.items() if k != 'password_hash'}
                    users.append(UserResponse(**user_data))

                return users

        except Exception as e:
            logger.error(f"Error searching users: {e}")
            raise

    def get_user_with_roles(self, user_id: int) -> Optional[UserWithRoles]:
        """
        Get user with their assigned roles.

        Args:
            user_id: User ID

        Returns:
            UserWithRoles or None
        """
        try:
            # Get user with roles via repository
            user_dict = self.user_repo.get_with_roles(user_id)
            if not user_dict:
                return None

            # Clean password_hash
            user_data = {k: v for k, v in user_dict.items() if k != 'password_hash'}

            # Convert roles array (if None, set to empty list)
            if user_data.get('roles') is None:
                user_data['roles'] = []

            return UserWithRoles(**user_data)

        except Exception as e:
            logger.error(f"Error getting user with roles {user_id}: {e}")
            raise

    def change_password(self, user_id: int, password_data: UserPasswordUpdate) -> bool:
        """
        Change user password.

        Args:
            user_id: User ID
            password_data: Password update data

        Returns:
            True if successful

        Raises:
            ValueError: If current password is incorrect
        """
        try:
            # Get current user with password hash
            user_dict = self.user_repo.get_by_id(user_id)

            if not user_dict:
                raise ValueError("User not found")

            # Verify current password
            if not self.password_service.verify_password(
                password_data.current_password,
                user_dict['password_hash']
            ):
                raise ValueError("Current password is incorrect")

            # Hash new password
            new_hash = self.password_service.hash_password(password_data.new_password)

            # Update password via repository
            success = self.user_repo.change_password(user_id, new_hash)

            if success:
                logger.info(f"Password changed for user ID: {user_id}")

            return success

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error changing password for user {user_id}: {e}")
            raise

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

    def get_all_users(
        self,
        include_deleted: bool = False,
        pagination: Optional[PaginationParams] = None
    ) -> List[UserResponse] | PaginatedResponse:
        """
        Get all users.

        Args:
            include_deleted: Include soft-deleted users
            pagination: Optional pagination

        Returns:
            List of UserResponse or PaginatedResponse
        """
        try:
            if pagination:
                # Get total count
                total = self.user_repo.count(include_deleted=include_deleted)

                # Get paginated items
                user_dicts = self.user_repo.get_all(
                    include_deleted=include_deleted,
                    limit=pagination.limit,
                    offset=pagination.offset
                )

                # Convert to schemas
                items = []
                for user_dict in user_dicts:
                    user_data = {k: v for k, v in user_dict.items() if k != 'password_hash'}
                    items.append(UserResponse(**user_data))

                return PaginatedResponse[UserResponse].create(
                    items=items,
                    total=total,
                    page=pagination.page,
                    page_size=pagination.page_size
                )
            else:
                user_dicts = self.user_repo.get_all(include_deleted=include_deleted)

                users = []
                for user_dict in user_dicts:
                    user_data = {k: v for k, v in user_dict.items() if k != 'password_hash'}
                    users.append(UserResponse(**user_data))

                return users

        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            raise

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
