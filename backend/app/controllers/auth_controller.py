from flask import request, jsonify, g, make_response, Blueprint
from pydantic import ValidationError

from app.middleware.cookie_handler import CookieManager
from app.middleware.error_handlers import ErrorResponse
import logging

logger = logging.getLogger(__name__)
auth_api = Blueprint('auth_api', __name__)

def get_auth_service():
    """
    Get auth service from request context (request-scoped injection).
    Follows DIP - dependency injected per request, not global coupling.
    """
    if not hasattr(g, 'auth_service'):
        from app.main import factory
        g.auth_service = factory.get_auth_service()
    return g.auth_service


@auth_api.route('/register', methods=['POST'])
def register_user():
    """
    Register a new user.

    Request Body:
        - username: str
        - email: str
        - password: str
        - role: str (optional)

    Returns:
        201: User registered successfully with auth cookie
        400: Validation error or user already exists
        500: Internal server error
    """
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return ErrorResponse.fail("Request body is required")

        # Get auth service (request-scoped injection)
        auth_service = get_auth_service()

        # Register user
        user_dict, token = auth_service.register(data)

        # Create success response
        response_data, status_code = ErrorResponse.success(
            data=user_dict,
            message='User registered successfully',
            status_code=201
        )
        response = make_response(response_data, status_code)

        # Set authentication cookie using middleware
        CookieManager.set_auth_cookie(response, token)

        return response

    except ValidationError as e:
        logger.warning(f"Registration validation error: {e.errors()}")
        return ErrorResponse.validation_error(e)
    except ValueError as e:
        logger.warning(f"Registration business logic error: {str(e)}")
        return ErrorResponse.fail(str(e))
    except Exception as e:
        logger.error(f"Registration failed: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Registration failed: {str(e)}')


@auth_api.route('/login', methods=['POST'])
def login_user():
    """
    Authenticate user and return token.

    Request Body:
        - email: str
        - password: str

    Returns:
        200: Login successful with auth cookie
        400: Invalid credentials or validation error
        500: Internal server error
    """
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return ErrorResponse.fail("Request body is required")

        # Get auth service (request-scoped injection)
        auth_service = get_auth_service()

        # Login user
        user_dict, token = auth_service.login(data)

        # Create success response
        response_data, status_code = ErrorResponse.success(
            data=user_dict,
            message='Login successful'
        )
        response = make_response(response_data, status_code)

        # Set authentication cookie using middleware
        CookieManager.set_auth_cookie(response, token)

        return response

    except ValidationError as e:
        logger.warning(f"Login validation error: {e.errors()}")
        return ErrorResponse.validation_error(e)
    except ValueError as e:
        logger.warning(f"Login failed: {str(e)}")
        return ErrorResponse.fail(str(e))
    except Exception as e:
        logger.error(f"Login error: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Login failed: {str(e)}')


@auth_api.route('/logout', methods=['POST'])
def logout_user():
    """
    Logout user by blacklisting token.

    Returns:
        200: Logout successful
        401: No authentication token found
        400: Logout failed
        500: Internal server error
    """
    try:
        # Get token from cookie
        token = request.cookies.get(CookieManager.AUTH_COOKIE_NAME)

        if not token:
            logger.warning("Logout attempted without token")
            return ErrorResponse.unauthorized('No authentication token found')

        # Get auth service (request-scoped injection)
        auth_service = get_auth_service()

        # Logout user
        result = auth_service.logout(token)

        if result:
            # Create success response
            response_data, status_code = ErrorResponse.success(
                message='Logout successful'
            )
            response = make_response(response_data, status_code)

            # Clear authentication cookies using middleware
            CookieManager.clear_all_auth_cookies(response)

            logger.info("User logged out successfully")
            return response
        else:
            logger.warning("Logout operation returned False")
            return ErrorResponse.fail('Logout failed')

    except ValueError as e:
        logger.warning(f"Logout business logic error: {str(e)}")
        return ErrorResponse.fail(str(e))
    except Exception as e:
        logger.error(f"Logout error: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Logout failed: {str(e)}')