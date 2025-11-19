from flask import request, jsonify
from . import auth_api

@auth_api.route('/register', methods=['POST'])
def register_user():
    """Register a new user"""
    try:
        # Get request data
        data = request.get_json()

        # Get auth service from factory (import lazily to avoid circular import)
        from app.main import factory
        auth_service = factory.get_auth_service()

        # Register user
        user_dict, token = auth_service.register(data)
        response = jsonify({
            'status': 'success',
            'message': 'User registered successfully',
            'data': user_dict
        })

        # Set token in HTTP-only cookie
        response.set_cookie(
            'access_token',
            token,
            httponly=True,      # Cannot be accessed by JavaScript (XSS protection)
            secure=False,       # Set to True in production with HTTPS
            samesite='Lax',     # CSRF protection
            max_age=3600        # 1 hour (same as token expiration)
        )

        return response, 201
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Registration failed: {str(e)}'
        }), 500


@auth_api.route('/login', methods=['POST'])
def login_user():
    """Authenticate user and return token"""
    try:
        # Get request data
        data = request.get_json()

        # Get auth service from factory (import lazily to avoid circular import)
        from app.main import factory
        auth_service = factory.get_auth_service()

        # Login user
        user_dict, token = auth_service.login(data)

        response = jsonify({
            'status': 'success',
            'message': 'Login successful',
            'data': user_dict
        })

        # Set token in HTTP-only cookie
        response.set_cookie(
            'access_token',
            token,
            httponly=True,      # Cannot be accessed by JavaScript (XSS protection)
            secure=False,       # Set to True in production with HTTPS
            samesite='Lax',     # CSRF protection
            max_age=3600        # 1 hour (same as token expiration)
        )

        return response, 200
    except Exception as e:
        # Log the actual error for debugging
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': f'Login failed: {str(e)}'
        }), 500


@auth_api.route('/logout', methods=['POST'])
def logout_user():
    """Logout user by blacklisting token"""
    try:
        # Get token from cookie
        token = request.cookies.get('access_token')

        if not token:
            return jsonify({
                'status': 'fail',
                'message': 'No authentication token found'
            }), 401

        # Get auth service from factory (import lazily to avoid circular import)
        from app.main import factory
        auth_service = factory.get_auth_service()

        # Logout user
        result = auth_service.logout(token)

        if result:
            response = jsonify({
                'status': 'success',
                'message': 'Logout successful'
            })

            # Clear the cookie
            response.set_cookie(
                'access_token',
                '',
                httponly=True,
                secure=False,
                samesite='Lax',
                max_age=0  # Expire immediately
            )

            return response, 200
        else:
            return jsonify({
                'status': 'fail',
                'message': 'Logout failed'
            }), 400

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': f'Logout failed: {str(e)}'
        }), 500