from flask import request, Blueprint, jsonify
from pydantic import ValidationError
from app.config.database import Database
from app.services.factory import ServiceFactory
from app.schemas.user_schemas import UserCreate, UserUpdate, UserSearchParams
from app.schemas.base_schema import PaginationParams
from app.middleware import token_required, admin_required
from typing import Dict, Any

# Create the Blueprint
user_api = Blueprint('user_api', __name__)

# Initialize service factory
db = Database()
factory = ServiceFactory(db)


@user_api.route('/users', methods=['POST'])
@token_required
@admin_required
def create_user(current_user):
    """Create a new user (admin operation)"""
    try:
        # Get request data
        data = request.get_json()

        # Get user service from factory
        user_service = factory.get_user_service()

        # Validate and create user
        user_data = UserCreate(**data)
        user = user_service.create_user(user_data)

        return jsonify({
            'status': 'success',
            'message': 'User created successfully',
            'data': user.model_dump()
        }), 201

    except ValidationError as e:
        return jsonify({
            'status': 'fail',
            'message': 'Validation error',
            'errors': e.errors()
        }), 400
    except ValueError as e:
        return jsonify({
            'status': 'fail',
            'message': str(e)
        }), 400
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': f'User creation failed: {str(e)}'
        }), 500


@user_api.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get user by ID"""
    try:
        user_service = factory.get_user_service()
        user = user_service.get_user(user_id)

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
            'message': f'Failed to get user: {str(e)}'
        }), 500


@user_api.route('/users', methods=['GET'])
def get_all_users():
    """Get all users with optional pagination"""
    try:
        user_service = factory.get_user_service()

        # Get pagination params from query string
        page = request.args.get('page', type=int)
        page_size = request.args.get('page_size', type=int)
        include_deleted = request.args.get('include_deleted', 'false').lower() == 'true'

        pagination = None
        if page and page_size:
            pagination = PaginationParams(page=page, page_size=page_size)

        result = user_service.get_all_users(
            include_deleted=include_deleted,
            pagination=pagination
        )

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

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': f'Failed to get users: {str(e)}'
        }), 500


@user_api.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Update user information"""
    try:
        data = request.get_json()
        user_service = factory.get_user_service()

        # Validate and update
        user_data = UserUpdate(**data)
        user = user_service.update_user(user_id, user_data)

        if not user:
            return jsonify({
                'status': 'fail',
                'message': 'User not found'
            }), 404

        return jsonify({
            'status': 'success',
            'message': 'User updated successfully',
            'data': user.model_dump()
        }), 200

    except ValidationError as e:
        return jsonify({
            'status': 'fail',
            'message': 'Validation error',
            'errors': e.errors()
        }), 400
    except ValueError as e:
        return jsonify({
            'status': 'fail',
            'message': str(e)
        }), 400
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': f'User update failed: {str(e)}'
        }), 500


@user_api.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Soft delete user"""
    try:
        user_service = factory.get_user_service()
        success = user_service.delete_user(user_id, hard_delete=False)

        if not success:
            return jsonify({
                'status': 'fail',
                'message': 'User not found'
            }), 404

        return jsonify({
            'status': 'success',
            'message': 'User deleted successfully'
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': f'User deletion failed: {str(e)}'
        }), 500


@user_api.route('/users/<int:user_id>/restore', methods=['POST'])
def restore_user(user_id):
    """Restore soft-deleted user"""
    try:
        user_service = factory.get_user_service()
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


@user_api.route('/users/search', methods=['GET'])
def search_users():
    """Search users with filters"""
    try:
        user_service = factory.get_user_service()

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


@user_api.route('/users/<int:user_id>/roles', methods=['GET'])
def get_user_with_roles(user_id):
    """Get user with their assigned roles"""
    try:
        user_service = factory.get_user_service()
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

