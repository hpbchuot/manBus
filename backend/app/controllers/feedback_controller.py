"""
Feedback Controller - Handles feedback-related HTTP endpoints.
Follows the same pattern as user_controller and auth_controller.
"""
from flask import request, Blueprint, jsonify, g
from pydantic import ValidationError
from app.middleware import token_required, admin_required
from app.middleware.error_handlers import ErrorResponse
import logging

logger = logging.getLogger(__name__)

# Create the Blueprint
feedback_api = Blueprint('feedback_api', __name__)


def get_feedback_service():
    """
    Get feedback service from request context (request-scoped injection).
    Follows DIP - dependency injected per request, not global coupling.
    """
    if not hasattr(g, 'feedback_service'):
        from app.main import factory
        g.feedback_service = factory.get_feedback_service()
    return g.feedback_service


@feedback_api.route('/', methods=['POST'])
@token_required
def create_feedback(current_user):
    """
    Create new feedback.

    Request Body:
        - bus_id: int
        - content: str (10-1000 characters)

    Returns:
        201: Feedback created successfully
        400: Validation error
        401: Unauthorized
        500: Internal server error
    """
    try:
        data = request.get_json()
        if not data:
            return ErrorResponse.fail("Request body is required")

        bus_id = data.get('bus_id')
        content = data.get('content')

        if not bus_id or not content:
            return ErrorResponse.fail("bus_id and content are required")

        feedback_service = get_feedback_service()
        feedback = feedback_service.create(
            user_id=current_user['id'],
            bus_id=bus_id,
            content=content
        )

        logger.info(f"Feedback created by user {current_user['id']}")
        return ErrorResponse.success(
            data=feedback,
            message='Feedback submitted successfully',
            status_code=201
        )

    except ValueError as e:
        logger.warning(f"Feedback creation error: {str(e)}")
        return ErrorResponse.fail(str(e))
    except Exception as e:
        logger.error(f"Feedback creation failed: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Feedback creation failed: {str(e)}')


@feedback_api.route('/<int:feedback_id>', methods=['GET'])
def get_feedback(feedback_id):
    """
    Get feedback by ID.

    Path Parameters:
        - feedback_id: int

    Returns:
        200: Feedback data
        404: Feedback not found
        500: Internal server error
    """
    try:
        feedback_service = get_feedback_service()
        feedback = feedback_service.get_by_id(feedback_id)

        if not feedback:
            logger.warning(f"Feedback not found: {feedback_id}")
            return ErrorResponse.not_found('Feedback')

        return ErrorResponse.success(data=feedback)

    except Exception as e:
        logger.error(f"Failed to get feedback {feedback_id}: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Failed to get feedback: {str(e)}')


@feedback_api.route('/user/<int:user_id>', methods=['GET'])
def get_user_feedback(user_id):
    """
    Get all feedback by user.

    Path Parameters:
        - user_id: int

    Query Parameters:
        - status: str (optional) - Pending, In Review, Resolved, Rejected

    Returns:
        200: List of feedback
        500: Internal server error
    """
    try:
        status = request.args.get('status')
        feedback_service = get_feedback_service()
        feedback_list = feedback_service.get_by_user(user_id, status)

        return ErrorResponse.success(data=feedback_list)

    except Exception as e:
        logger.error(f"Failed to get user feedback: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Failed to get user feedback: {str(e)}')


@feedback_api.route('/bus/<int:bus_id>', methods=['GET'])
def get_bus_feedback(bus_id):
    """
    Get all feedback for a bus.

    Path Parameters:
        - bus_id: int

    Query Parameters:
        - status: str (optional)

    Returns:
        200: List of feedback
        500: Internal server error
    """
    try:
        status = request.args.get('status')
        feedback_service = get_feedback_service()
        feedback_list = feedback_service.get_by_bus(bus_id, status)

        return ErrorResponse.success(data=feedback_list)

    except Exception as e:
        logger.error(f"Failed to get bus feedback: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Failed to get bus feedback: {str(e)}')


@feedback_api.route('/route/<int:route_id>', methods=['GET'])
def get_route_feedback(route_id):
    """
    Get all feedback for a route.

    Path Parameters:
        - route_id: int

    Query Parameters:
        - status: str (optional)

    Returns:
        200: List of feedback
        500: Internal server error
    """
    try:
        status = request.args.get('status')
        feedback_service = get_feedback_service()
        feedback_list = feedback_service.get_by_route(route_id, status)

        return ErrorResponse.success(data=feedback_list)

    except Exception as e:
        logger.error(f"Failed to get route feedback: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Failed to get route feedback: {str(e)}')


@feedback_api.route('/pending', methods=['GET'])
@token_required
@admin_required
def get_pending_feedback(current_user):
    """
    Get all pending feedback (admin only).

    Returns:
        200: List of pending feedback
        401: Unauthorized
        403: Forbidden
        500: Internal server error
    """
    try:
        feedback_service = get_feedback_service()
        feedback_list = feedback_service.get_pending_feedback()

        return ErrorResponse.success(data=feedback_list)

    except Exception as e:
        logger.error(f"Failed to get pending feedback: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Failed to get pending feedback: {str(e)}')


@feedback_api.route('/', methods=['GET'])
@token_required
@admin_required
def get_all_feedback(current_user):
    """
    Get all feedback with optional filtering (admin only).

    Query Parameters:
        - status: str (optional)
        - limit: int (default: 100)
        - offset: int (default: 0)

    Returns:
        200: List of feedback
        401: Unauthorized
        403: Forbidden
        500: Internal server error
    """
    try:
        status = request.args.get('status')
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)

        feedback_service = get_feedback_service()
        feedback_list = feedback_service.get_all(status, limit, offset)

        return ErrorResponse.success(data=feedback_list)

    except Exception as e:
        logger.error(f"Failed to get all feedback: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Failed to get all feedback: {str(e)}')


@feedback_api.route('/recent', methods=['GET'])
def get_recent_feedback():
    """
    Get recent feedback entries.

    Query Parameters:
        - days: int (default: 7)
        - limit: int (default: 50)

    Returns:
        200: List of recent feedback
        500: Internal server error
    """
    try:
        days = request.args.get('days', 7, type=int)
        limit = request.args.get('limit', 50, type=int)

        feedback_service = get_feedback_service()
        feedback_list = feedback_service.get_recent_feedback(days, limit)

        return ErrorResponse.success(data=feedback_list)

    except ValueError as e:
        logger.warning(f"Recent feedback error: {str(e)}")
        return ErrorResponse.fail(str(e))
    except Exception as e:
        logger.error(f"Failed to get recent feedback: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Failed to get recent feedback: {str(e)}')


@feedback_api.route('/statistics', methods=['GET'])
@token_required
@admin_required
def get_feedback_statistics(current_user):
    """
    Get feedback statistics (admin only).

    Returns:
        200: Statistics data
        401: Unauthorized
        403: Forbidden
        500: Internal server error
    """
    try:
        feedback_service = get_feedback_service()
        stats = feedback_service.get_statistics()

        return ErrorResponse.success(data=stats)

    except Exception as e:
        logger.error(f"Failed to get feedback statistics: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Failed to get feedback statistics: {str(e)}')


@feedback_api.route('/<int:feedback_id>/status', methods=['PUT'])
@token_required
@admin_required
def update_feedback_status(current_user, feedback_id):
    """
    Update feedback status (admin only).

    Path Parameters:
        - feedback_id: int

    Request Body:
        - status: str (Pending, In Review, Resolved, Rejected)

    Returns:
        200: Status updated successfully
        400: Validation error
        401: Unauthorized
        403: Forbidden
        404: Feedback not found
        500: Internal server error
    """
    try:
        data = request.get_json()
        if not data or 'status' not in data:
            return ErrorResponse.fail("status is required")

        feedback_service = get_feedback_service()
        success = feedback_service.update_status(feedback_id, data['status'])

        if success:
            logger.info(f"Feedback {feedback_id} status updated by admin {current_user['id']}")
            return ErrorResponse.success(message='Feedback status updated successfully')
        else:
            return ErrorResponse.fail('Failed to update feedback status')

    except ValueError as e:
        logger.warning(f"Status update error: {str(e)}")
        return ErrorResponse.fail(str(e))
    except Exception as e:
        logger.error(f"Status update failed: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Status update failed: {str(e)}')


@feedback_api.route('/<int:feedback_id>/content', methods=['PUT'])
@token_required
def update_feedback_content(current_user, feedback_id):
    """
    Update feedback content (user can only edit their own pending feedback).

    Path Parameters:
        - feedback_id: int

    Request Body:
        - content: str (10-1000 characters)

    Returns:
        200: Content updated successfully
        400: Validation error
        401: Unauthorized
        404: Feedback not found
        500: Internal server error
    """
    try:
        data = request.get_json()
        if not data or 'content' not in data:
            return ErrorResponse.fail("content is required")

        feedback_service = get_feedback_service()
        success = feedback_service.update_content(
            feedback_id,
            current_user['id'],
            data['content']
        )

        if success:
            logger.info(f"Feedback {feedback_id} content updated by user {current_user['id']}")
            return ErrorResponse.success(message='Feedback content updated successfully')
        else:
            return ErrorResponse.fail('Failed to update feedback content')

    except ValueError as e:
        logger.warning(f"Content update error: {str(e)}")
        return ErrorResponse.fail(str(e))
    except Exception as e:
        logger.error(f"Content update failed: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Content update failed: {str(e)}')


@feedback_api.route('/<int:feedback_id>', methods=['DELETE'])
@token_required
def delete_feedback(current_user, feedback_id):
    """
    Delete feedback.
    Users can only delete their own pending feedback.
    Admins can delete any feedback.

    Path Parameters:
        - feedback_id: int

    Returns:
        200: Feedback deleted successfully
        401: Unauthorized
        404: Feedback not found
        500: Internal server error
    """
    try:
        feedback_service = get_feedback_service()

        # Check if user is admin
        user_id = None if current_user.get('admin') else current_user['id']

        success = feedback_service.delete(feedback_id, user_id)

        if success:
            logger.info(f"Feedback {feedback_id} deleted by user {current_user['id']}")
            return ErrorResponse.success(message='Feedback deleted successfully')
        else:
            return ErrorResponse.fail('Failed to delete feedback')

    except ValueError as e:
        logger.warning(f"Feedback deletion error: {str(e)}")
        return ErrorResponse.fail(str(e))
    except Exception as e:
        logger.error(f"Feedback deletion failed: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Feedback deletion failed: {str(e)}')
