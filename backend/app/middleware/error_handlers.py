"""
Centralized Error Handling Middleware
Provides consistent error responses across all controllers.

Follows SOLID principles:
- SRP: Single responsibility - error handling and formatting
- OCP: Extensible for new error types
- ISP: Focused interface for error handling
"""
from flask import jsonify, Blueprint
from pydantic import ValidationError
from typing import Dict, Any, Tuple
import logging
import traceback

logger = logging.getLogger(__name__)


class ErrorResponse:
    """
    Standardized error response builder.
    Single Responsibility: Format error responses consistently.
    """

    @staticmethod
    def success(data: Any = None, message: str = "Success", status_code: int = 200) -> Tuple[Dict, int]:
        """
        Create a success response.

        Args:
            data: Response data
            message: Success message
            status_code: HTTP status code

        Returns:
            Tuple of (response_dict, status_code)
        """
        response = {
            'status': 'success',
            'message': message
        }
        if data is not None:
            response['data'] = data
        return jsonify(response), status_code

    @staticmethod
    def fail(message: str, errors: Any = None, status_code: int = 400) -> Tuple[Dict, int]:
        """
        Create a fail response (client error).

        Args:
            message: Error message
            errors: Optional error details
            status_code: HTTP status code

        Returns:
            Tuple of (response_dict, status_code)
        """
        response = {
            'status': 'fail',
            'message': message
        }
        if errors is not None:
            response['errors'] = errors
        return jsonify(response), status_code

    @staticmethod
    def error(message: str, status_code: int = 500) -> Tuple[Dict, int]:
        """
        Create an error response (server error).

        Args:
            message: Error message
            status_code: HTTP status code

        Returns:
            Tuple of (response_dict, status_code)
        """
        return jsonify({
            'status': 'error',
            'message': message
        }), status_code

    @staticmethod
    def validation_error(validation_error: ValidationError) -> Tuple[Dict, int]:
        """
        Create a validation error response from Pydantic ValidationError.

        Args:
            validation_error: Pydantic ValidationError instance

        Returns:
            Tuple of (response_dict, status_code)
        """
        return jsonify({
            'status': 'fail',
            'message': 'Validation error',
            'errors': validation_error.errors()
        }), 400

    @staticmethod
    def not_found(resource: str = "Resource") -> Tuple[Dict, int]:
        """
        Create a not found response.

        Args:
            resource: Name of the resource not found

        Returns:
            Tuple of (response_dict, status_code)
        """
        return jsonify({
            'status': 'fail',
            'message': f'{resource} not found'
        }), 404

    @staticmethod
    def unauthorized(message: str = "Unauthorized") -> Tuple[Dict, int]:
        """
        Create an unauthorized response.

        Args:
            message: Error message

        Returns:
            Tuple of (response_dict, status_code)
        """
        return jsonify({
            'status': 'fail',
            'message': message
        }), 401

    @staticmethod
    def forbidden(message: str = "Forbidden") -> Tuple[Dict, int]:
        """
        Create a forbidden response.

        Args:
            message: Error message

        Returns:
            Tuple of (response_dict, status_code)
        """
        return jsonify({
            'status': 'fail',
            'message': message
        }), 403


def register_error_handlers(app):
    """
    Register global error handlers for the Flask app.

    Args:
        app: Flask application instance
    """

    @app.errorhandler(ValidationError)
    def handle_validation_error(e: ValidationError):
        """Handle Pydantic validation errors globally"""
        logger.warning(f"Validation error: {e.errors()}")
        return ErrorResponse.validation_error(e)

    @app.errorhandler(ValueError)
    def handle_value_error(e: ValueError):
        """Handle business logic ValueError"""
        logger.warning(f"ValueError: {str(e)}")
        return ErrorResponse.fail(str(e))

    @app.errorhandler(404)
    def handle_not_found(e):
        """Handle 404 errors"""
        return ErrorResponse.not_found()

    @app.errorhandler(401)
    def handle_unauthorized(e):
        """Handle 401 unauthorized errors"""
        return ErrorResponse.unauthorized()

    @app.errorhandler(403)
    def handle_forbidden(e):
        """Handle 403 forbidden errors"""
        return ErrorResponse.forbidden()

    @app.errorhandler(500)
    def handle_internal_error(e):
        """Handle 500 internal server errors"""
        logger.error(f"Internal server error: {str(e)}")
        logger.error(traceback.format_exc())
        return ErrorResponse.error("Internal server error")

    @app.errorhandler(Exception)
    def handle_generic_exception(e: Exception):
        """Handle any unhandled exceptions"""
        logger.error(f"Unhandled exception: {str(e)}")
        logger.error(traceback.format_exc())
        return ErrorResponse.error(f"An unexpected error occurred: {str(e)}")


def create_error_handler_blueprint() -> Blueprint:
    """
    Create a blueprint for error handlers that can be registered with specific blueprints.

    Returns:
        Flask Blueprint with error handlers
    """
    error_bp = Blueprint('errors', __name__)

    @error_bp.app_errorhandler(ValidationError)
    def handle_validation_error(e: ValidationError):
        """Handle Pydantic validation errors"""
        logger.warning(f"Validation error: {e.errors()}")
        return ErrorResponse.validation_error(e)

    @error_bp.app_errorhandler(ValueError)
    def handle_value_error(e: ValueError):
        """Handle business logic ValueError"""
        logger.warning(f"ValueError: {str(e)}")
        return ErrorResponse.fail(str(e))

    return error_bp


# Custom exceptions for domain-specific errors
class DomainException(Exception):
    """Base exception for domain errors"""
    pass


class EntityNotFoundException(DomainException):
    """Raised when an entity is not found"""
    def __init__(self, entity_type: str, entity_id: Any):
        self.entity_type = entity_type
        self.entity_id = entity_id
        super().__init__(f"{entity_type} with id {entity_id} not found")


class UnauthorizedException(DomainException):
    """Raised when user is not authorized"""
    pass


class ForbiddenException(DomainException):
    """Raised when user doesn't have permission"""
    pass


class ValidationException(DomainException):
    """Raised when business validation fails"""
    pass


class ServiceException(DomainException):
    """Raised when a service operation fails"""
    pass
