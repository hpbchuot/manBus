from flask import request, Blueprint, jsonify, g
from pydantic import ValidationError
from app.schemas.user_schemas import UserCreate, UserUpdate, UserSearchParams
from app.schemas.base_schema import PaginationParams
from app.middleware import token_required, admin_required
from app.middleware.error_handlers import ErrorResponse
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

# Create the Blueprint
user_api = Blueprint('user_api', __name__)


def get_user_service():
    """
    Get user service from request context (request-scoped injection).
    Follows DIP - dependency injected per request, not global coupling.
    """
    if not hasattr(g, 'user_service'):
        from app.main import factory
        g.user_service = factory.get_user_service()
    return g.user_service


@user_api.route('/', methods=['POST'])
@token_required
@admin_required
def create_user(current_user):
    """
    Create a new user (admin operation).

    Request Body:
        - username: str
        - email: str
        - password: str
        - role: str (optional)

    Returns:
        201: User created successfully
        400: Validation error or user already exists
        401: Unauthorized
        403: Forbidden (non-admin)
        500: Internal server error
    """
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return ErrorResponse.fail("Request body is required")

        # Get user service (request-scoped injection)
        user_service = get_user_service()

        # Validate and create user
        user_data = UserCreate(**data)
        user = user_service.create_user(user_data)

        logger.info(f"User created successfully: {user.user_id}")
        return ErrorResponse.success(
            data=user.model_dump(),
            message='User created successfully',
            status_code=201
        )

    except ValidationError as e:
        logger.warning(f"User creation validation error: {e.errors()}")
        return ErrorResponse.validation_error(e)
    except ValueError as e:
        logger.warning(f"User creation business logic error: {str(e)}")
        return ErrorResponse.fail(str(e))
    except Exception as e:
        logger.error(f"User creation failed: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'User creation failed: {str(e)}')


@user_api.route('/by/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """
    Get user by ID.

    Path Parameters:
        - user_id: int

    Returns:
        200: User data
        404: User not found
        500: Internal server error
    """
    try:
        user_service = get_user_service()
        user = user_service.get_user(user_id)

        if not user:
            logger.warning(f"User not found: {user_id}")
            return ErrorResponse.not_found('User')

        return ErrorResponse.success(data=user.model_dump())

    except Exception as e:
        logger.error(f"Failed to get user {user_id}: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Failed to get user: {str(e)}')


@user_api.route('/', methods=['GET'])
@token_required
@admin_required
def get_all_users(current_user):
    """
    Get all users with cursor-based pagination.

    Query Parameters:
        - cursor: int (optional) - User ID from last result for pagination
        - limit: int (optional) - Number of results (default 20, max 100)
        - role: str (optional) - Filter by role (User, Driver, Admin)
        - include_deleted: bool (optional) - Include soft-deleted users

    Returns:
        200: List of users
        401: Unauthorized
        403: Forbidden (non-admin)
        500: Internal server error
    """
    try:
        user_service = get_user_service()

        # Get query parameters
        cursor = request.args.get('cursor', type=int)
        limit = request.args.get('limit', type=int, default=20)
        role = request.args.get('role', type=str)
        include_deleted = request.args.get('include_deleted', 'false').lower() == 'true'

        # Get users with cursor-based pagination
        users = user_service.get_all_users(
            cursor=cursor,
            limit=limit,
            role=role,
            include_deleted=include_deleted
        )

        # Convert to dict for JSON response
        users_data = [user.model_dump() for user in users]

        # Calculate next cursor (last user's ID if results exist)
        next_cursor = users_data[-1]['id'] if users_data else None
        has_more = len(users_data) == limit  # If we got exactly limit, there might be more

        return ErrorResponse.success(
            data={
                'users': users_data,
                'has_more': has_more,
                'next_cursor': next_cursor,
                'count': len(users_data)
            }
        )

    except Exception as e:
        logger.error(f"Failed to get users: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Failed to get users: {str(e)}')


@user_api.route('/by/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """
    Update user information.

    Path Parameters:
        - user_id: int

    Request Body:
        - username: str (optional)
        - email: str (optional)
        - password: str (optional)
        - role: str (optional)

    Returns:
        200: User updated successfully
        400: Validation error
        404: User not found
        500: Internal server error
    """
    try:
        data = request.get_json()
        if not data:
            return ErrorResponse.fail("Request body is required")

        user_service = get_user_service()

        # Validate and update
        user_data = UserUpdate(**data)
        user = user_service.update_user(user_id, user_data)

        if not user:
            logger.warning(f"User not found for update: {user_id}")
            return ErrorResponse.not_found('User')

        logger.info(f"User updated successfully: {user_id}")
        return ErrorResponse.success(
            data=user.model_dump(),
            message='User updated successfully'
        )

    except ValidationError as e:
        logger.warning(f"User update validation error: {e.errors()}")
        return ErrorResponse.validation_error(e)
    except ValueError as e:
        logger.warning(f"User update business logic error: {str(e)}")
        return ErrorResponse.fail(str(e))
    except Exception as e:
        logger.error(f"User update failed: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'User update failed: {str(e)}')


@user_api.route('/by/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """
    Soft delete user.

    Path Parameters:
        - user_id: int

    Returns:
        200: User deleted successfully
        404: User not found
        500: Internal server error
    """
    try:
        user_service = get_user_service()
        success = user_service.delete_user(user_id, hard_delete=False)

        if not success:
            logger.warning(f"User not found for deletion: {user_id}")
            return ErrorResponse.not_found('User')

        logger.info(f"User soft deleted successfully: {user_id}")
        return ErrorResponse.success(message='User deleted successfully')

    except ValueError as e:
        logger.warning(f"User deletion business logic error: {str(e)}")
        return ErrorResponse.fail(str(e))
    except Exception as e:
        logger.error(f"User deletion failed: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'User deletion failed: {str(e)}')


@user_api.route('/restore/by/<int:user_id>', methods=['POST'])
def restore_user(user_id):
    """Restore soft-deleted user"""
    try:
        user_service = get_user_service()
        user = user_service.restore_user(user_id)

        if not user:
            return jsonify({
                'status': 'fail',
                'message': 'User not found'
            }), 404

        return jsonify({
            'status': 'success',
            'message': 'User restored successfully',
            'data': user.model_dump()
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': f'User restoration failed: {str(e)}'
        }), 500


@user_api.route('/search', methods=['GET'])
def search_users():
    """Search users with filters"""
    try:
        user_service = get_user_service()

        # Get search params
        query = request.args.get('query')
        admin_only = request.args.get('admin_only', 'false').lower() == 'true'
        include_deleted = request.args.get('include_deleted', 'false').lower() == 'true'

        # Get pagination params
        page = request.args.get('page', type=int)
        page_size = request.args.get('page_size', type=int)

        search_params = UserSearchParams(
            query=query,
            admin_only=admin_only,
            include_deleted=include_deleted
        )

        pagination = None
        if page and page_size:
            pagination = PaginationParams(page=page, page_size=page_size)

        result = user_service.search_users(search_params, pagination)

        # Handle paginated vs non-paginated response
        if pagination:
            return jsonify({
                'status': 'success',
                'data': result.model_dump()
            }), 200
        else:
            return jsonify({
                'status': 'success',
                'data': [user.model_dump() for user in result]
            }), 200

    except ValidationError as e:
        return jsonify({
            'status': 'fail',
            'message': 'Validation error',
            'errors': e.errors()
        }), 400
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': f'User search failed: {str(e)}'
        }), 500


@user_api.route('/by/<int:user_id>/roles', methods=['GET'])
def get_user_with_roles(user_id):
    """Get user with their assigned roles"""
    try:
        user_service = get_user_service()
        user = user_service.get_user_with_roles(user_id)

        if not user:
            return jsonify({
                'status': 'fail',
                'message': 'User not found'
            }), 404

        return jsonify({
            'status': 'success',
            'data': user.model_dump()
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': f'Failed to get user roles: {str(e)}'
        }), 500

