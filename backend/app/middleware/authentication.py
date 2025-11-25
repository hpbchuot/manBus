from functools import wraps
from flask import jsonify
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

        # Step 3: Check if token is blacklisted (using factory)
        try:
            from app.main import factory
            token_service = factory.get_token_service()
            if token_service.is_blacklisted(token):
                return jsonify({
                    'message': 'Token blacklisted. Please log in again.',
                    'status': 'fail'
                }), 401

        except Exception as e:
            logger.error(f"Blacklist check error: {e}")
            return jsonify({
                'message': 'Authentication failed',
                'status': 'fail'
            }), 500

        # Step 4: Get user from database (using factory)
        try:
            from app.main import factory
            user_repo = factory.get_user_repository()
            current_user = user_repo.get_by_id(payload['user_id'])

            if not current_user:
                return jsonify({
                    'message': 'User not found or has been deleted',
                    'status': 'fail'
                }), 401

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
        if current_user.get('role') != 'Admin':
            return jsonify({
                'message': 'Admin privileges required',
                'status': 'fail'
            }), 403

        return f(current_user, *args, **kwargs)

    return decorated

