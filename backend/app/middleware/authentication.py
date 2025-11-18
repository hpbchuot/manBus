from functools import wraps
from flask import request, jsonify
import jwt
from ..config import key
import logging

logger = logging.getLogger(__name__)

def token_required(f):
    """
    Decorator for routes that require authentication.
    Validates JWT token and injects user data into the request.

    Usage:
        @app.route('/protected')
        @token_required
        def protected_route(current_user):
            return jsonify({'message': f'Hello {current_user["username"]}'})
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Check for token in Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                # Expected format: "Bearer <token>"
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({
                    'message': 'Invalid token format. Use "Bearer <token>"',
                    'status': 'fail'
                }), 401

        # Check for token in request args (query parameters)
        if not token and 'token' in request.args:
            token = request.args.get('token')

        # No token found
        if not token:
            return jsonify({
                'message': 'Authentication token is missing',
                'status': 'fail'
            }), 401

        try:
            # Decode the token
            payload = jwt.decode(token, key, algorithms=['HS256'])

            # Check if token is blacklisted (if you implement blacklist)
            from flask import current_app
            db = current_app.config['db']
            blacklist_check = db.fetch_one(
                "SELECT * FROM blacklist_token WHERE token = %s",
                (token,)
            )

            if blacklist_check:
                return jsonify({
                    'message': 'Token blacklisted. Please log in again.',
                    'status': 'fail'
                }), 401

            # Get user from database
            current_user = db.fetch_one(
                """SELECT id, public_id, username, email, name, phone,
                          admin, role, registered_on, isdeleted
                   FROM "user" WHERE public_id = %s AND isdeleted = false""",
                (payload['uuid'],)
            )

            if not current_user:
                return jsonify({
                    'message': 'User not found or has been deleted',
                    'status': 'fail'
                }), 401

            # Convert RealDictRow to regular dict for easier access
            current_user = dict(current_user)

        except jwt.ExpiredSignatureError:
            return jsonify({
                'message': 'Token has expired. Please log in again.',
                'status': 'fail'
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                'message': 'Invalid token. Please log in again.',
                'status': 'fail'
            }), 401
        except Exception as e:
            logger.error(f"Authentication error: {e}")
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

