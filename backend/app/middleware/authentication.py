from functools import wraps
from flask import jsonify, current_app
from .token_extractor import TokenExtractor
from .token_validator import TokenValidator
from ..config import JWT_SECRET_KEY
import logging

logger = logging.getLogger(__name__)

# Initialize token validator with secret key
_token_validator = TokenValidator(JWT_SECRET_KEY)


def token_required(f):
    """
    Decorator for routes that require authentication.
    Validates JWT token and injects user data into the request.

    This decorator now follows SRP by delegating to specialized classes:
    - TokenExtractor: Extract token from request
    - TokenValidator: Validate JWT structure
    - Database services: Check blacklist and retrieve user

    Usage:
        @app.route('/protected')
        @token_required
        def protected_route(current_user):
            return jsonify({'message': f'Hello {current_user["username"]}'})
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # Step 1: Extract token (delegated to TokenExtractor)
        token, error, status = TokenExtractor.extract_from_request()
        if error:
            return jsonify(error), status

        # Step 2: Validate token structure (delegated to TokenValidator)
        payload, error, status = _token_validator.validate(token)
        if error:
            return jsonify(error), status

        # Step 3: Check if token is blacklisted (using dependency container)
        try:
            container = current_app.config.get('container')
            if container:
                blacklist_service = container.get_blacklist_service()
                if blacklist_service.is_blacklisted(token):
                    return jsonify({
                        'message': 'Token blacklisted. Please log in again.',
                        'status': 'fail'
                    }), 401
            else:
                # Fallback to direct database access using database function
                db = current_app.config['db']
                blacklist_check = db.fetch_one(
                    "SELECT fn_is_token_blacklisted(%s) AS is_blacklisted",
                    (token,)
                )
                if blacklist_check and blacklist_check['is_blacklisted']:
                    return jsonify({
                        'message': 'Token blacklisted. Please log in again.',
                        'status': 'fail'
                    }), 401

        except Exception as e:
            logger.error(f"Blacklist check error: {e}")

        # Step 4: Get user from database (using repository if available)
        try:
            container = current_app.config.get('container')
            if container:
                user_repo = container.get_user_repository()
                current_user = user_repo.get_by_id(payload['uuid'])
                if not current_user:
                    return jsonify({
                        'message': 'User not found or has been deleted',
                        'status': 'fail'
                    }), 401
                current_user = dict(current_user[0]) if isinstance(current_user, list) else dict(current_user)
            else:
                # Fallback to direct database access
                db = current_app.config['db']
                current_user = db.fetch_one(
                    """SELECT id, public_id, username, email, name, phone,
                              admin, registered_on, is_deleted
                       FROM Users WHERE public_id = %s AND is_deleted = false""",
                    (payload['uuid'],)
                )
                if not current_user:
                    return jsonify({
                        'message': 'User not found or has been deleted',
                        'status': 'fail'
                    }), 401
                current_user = dict(current_user)

        except Exception as e:
            logger.error(f"User retrieval error: {e}")
            return jsonify({
                'message': 'Authentication failed',
                'status': 'fail'
            }), 500

        # Pass the current_user to the decorated function
        return f(current_user, *args, **kwargs)

    return decorated


def admin_required(f):
    """
    Decorator for routes that require admin privileges.
    Must be used in combination with @token_required.

    Usage:
        @app.route('/admin')
        @token_required
        @admin_required
        def admin_route(current_user):
            return jsonify({'message': 'Admin access granted'})
    """
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if not current_user.get('admin', False):
            return jsonify({
                'message': 'Admin privileges required',
                'status': 'fail'
            }), 403

        return f(current_user, *args, **kwargs)

    return decorated


def role_required(required_role):
    """
    Decorator for routes that require a specific role level.
    Must be used in combination with @token_required.

    Args:
        required_role: Minimum role level required (integer)

    Usage:
        @app.route('/manager')
        @token_required
        @role_required(2)
        def manager_route(current_user):
            return jsonify({'message': 'Manager access granted'})
    """
    def decorator(f):
        @wraps(f)
        def decorated(current_user, *args, **kwargs):
            user_role = current_user.get('role', 1)

            if user_role < required_role:
                return jsonify({
                    'message': f'Role level {required_role} or higher required',
                    'status': 'fail'
                }), 403

            return f(current_user, *args, **kwargs)

        return decorated
    return decorator

