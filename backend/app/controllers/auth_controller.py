from flask import request, Blueprint, jsonify
from app.core.dependencies import get_container

auth_api = Blueprint('auth_api', __name__)

@auth_api.route('/register', methods=['POST'])
def register_user():
    """Register a new user"""
    try:
        # Get request data
        data = request.get_json()

        # Get auth service from dependency container
        container = get_container()
        auth_service = container.get_auth_service()

        # Register user
        user = auth_service.register(data)

        if user:
            return jsonify({
                'status': 'success',
                'message': 'User registered successfully',
                'data': user.toJson() if hasattr(user, 'toJson') else user.__dict__
            }), 201
        else:
            return jsonify({
                'status': 'fail',
                'message': 'User registration failed'
            }), 400

    except Exception as e:
        return jsonify({
            'status': 'fail',
            'message': str(e)
        }), 400


@auth_api.route('/login', methods=['POST'])
def login_user():
    """Authenticate user and return token"""
    try:
        # Get request data
        data = request.get_json()

        # Get auth service from dependency container
        container = get_container()
        auth_service = container.get_auth_service()

        # Login user
        result = auth_service.login(data)

        return jsonify({
            'status': 'success',
            'message': 'Login successful',
            'data': {
                'token': result['token'],
                'expires_in': result['expires_in'],
                'user': result['user'].toJson() if hasattr(result['user'], 'toJson') else result['user'].__dict__
            }
        }), 200

    except ValueError as e:
        return jsonify({
            'status': 'fail',
            'message': str(e)
        }), 401
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
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({
                'status': 'fail',
                'message': 'Authorization header missing'
            }), 401

        # Extract token
        token = auth_header.split(" ")[1] if " " in auth_header else auth_header

        # Get auth service from dependency container
        container = get_container()
        auth_service = container.get_auth_service()

        # Logout user
        result = auth_service.logout(token)

        return jsonify({
            'status': 'success',
            'message': result['message']
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'fail',
            'message': str(e)
        }), 500

# @auth_api.route('/refresh-token', methods=['POST'])
# @api.validate(
#     body=Request(RefreshTokenDTO),  # Validate the request body using the Pydantic model
#     resp=Response(HTTP_200=Message, HTTP_400=Message),  # Example response
#     tags=['auth']
# )
# def refresh_token():
#     data = request.context.body
#     return Auth.get_refresh_token(data=data)
#
#
# @api.route('/logout')
# class LogoutAPI(Resource):
#     """
#     Logout Resource
#     """
#     @api.doc('logout a user')
#     def post(self):
#         # get auth token
#         auth_header = request.headers.get('Authorization')
#         return Auth.logout_user(data=auth_header)