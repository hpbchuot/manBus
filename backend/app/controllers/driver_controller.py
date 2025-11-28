"""
Driver Controller - Handles driver-related HTTP endpoints.
Follows the same pattern as user_controller and auth_controller.
"""
from flask import request, Blueprint, jsonify, g
from pydantic import ValidationError
from app.middleware import token_required, admin_required
from app.middleware.error_handlers import ErrorResponse
import logging

logger = logging.getLogger(__name__)

# Create the Blueprint
driver_api = Blueprint('driver_api', __name__)


def get_driver_service():
    """
    Get driver service from request context (request-scoped injection).
    Follows DIP - dependency injected per request, not global coupling.
    """
    if not hasattr(g, 'driver_service'):
        from app.main import factory
        g.driver_service = factory.get_driver_service()
    return g.driver_service


@driver_api.route('/', methods=['POST'])
@token_required
@admin_required
def create_driver(current_user):
    """
    Create a new driver (admin operation).

    Request Body:
        - user_id: int
        - license_number: str (min 5 characters)
        - bus_id: int

    Returns:
        201: Driver created successfully
        400: Validation error
        401: Unauthorized
        403: Forbidden
        500: Internal server error
    """
    try:
        data = request.get_json()
        if not data:
            return ErrorResponse.fail("Request body is required")

        user_id = data.get('user_id')
        license_number = data.get('license_number')
        bus_id = data.get('bus_id')

        if not all([user_id, license_number, bus_id]):
            return ErrorResponse.fail("user_id, license_number, and bus_id are required")

        driver_service = get_driver_service()
        driver = driver_service.create(user_id, license_number, bus_id)

        logger.info(f"Driver created successfully: {driver.get('id')}")
        return ErrorResponse.success(
            data=driver,
            message='Driver created successfully',
            status_code=201
        )

    except ValueError as e:
        logger.warning(f"Driver creation error: {str(e)}")
        return ErrorResponse.fail(str(e))
    except Exception as e:
        logger.error(f"Driver creation failed: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Driver creation failed: {str(e)}')


@driver_api.route('/<int:driver_id>', methods=['GET'])
def get_driver(driver_id):
    """
    Get driver by ID.

    Path Parameters:
        - driver_id: int

    Returns:
        200: Driver data
        404: Driver not found
        500: Internal server error
    """
    try:
        driver_service = get_driver_service()
        driver = driver_service.get_by_id(driver_id)

        if not driver:
            logger.warning(f"Driver not found: {driver_id}")
            return ErrorResponse.not_found('Driver')

        return ErrorResponse.success(data=driver)

    except Exception as e:
        logger.error(f"Failed to get driver {driver_id}: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Failed to get driver: {str(e)}')


@driver_api.route('/user/<int:user_id>', methods=['GET'])
def get_driver_by_user(user_id):
    """
    Get driver by user ID.

    Path Parameters:
        - user_id: int

    Returns:
        200: Driver data with bus and route information
        404: Driver not found
        500: Internal server error
    """
    try:
        driver_service = get_driver_service()
        driver = driver_service.get_by_user_id(user_id)

        if not driver:
            logger.warning(f"Driver not found for user: {user_id}")
            return ErrorResponse.not_found('Driver')

        return ErrorResponse.success(data=driver)

    except Exception as e:
        logger.error(f"Failed to get driver by user: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Failed to get driver: {str(e)}')


@driver_api.route('/bus/<int:bus_id>', methods=['GET'])
def get_driver_by_bus(bus_id):
    """
    Get driver assigned to a specific bus.

    Path Parameters:
        - bus_id: int

    Returns:
        200: Driver data
        404: Driver not found
        500: Internal server error
    """
    try:
        driver_service = get_driver_service()
        driver = driver_service.get_by_bus_id(bus_id)

        if not driver:
            logger.warning(f"Driver not found for bus: {bus_id}")
            return ErrorResponse.not_found('Driver')

        return ErrorResponse.success(data=driver)

    except Exception as e:
        logger.error(f"Failed to get driver by bus: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Failed to get driver: {str(e)}')


@driver_api.route('/active', methods=['GET'])
def get_active_drivers():
    """
    Get all active drivers.

    Returns:
        200: List of active drivers with user, bus, and route information
        500: Internal server error
    """
    try:
        driver_service = get_driver_service()
        drivers = driver_service.get_all_active()

        return ErrorResponse.success(data=drivers)

    except Exception as e:
        logger.error(f"Failed to get active drivers: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Failed to get active drivers: {str(e)}')


@driver_api.route('/', methods=['GET'])
def get_all_drivers():
    """
    Get all drivers.

    Query Parameters:
        - include_deleted_users: bool (default: false)

    Returns:
        200: List of drivers
        500: Internal server error
    """
    try:
        include_deleted = request.args.get('include_deleted_users', 'false').lower() == 'true'

        driver_service = get_driver_service()
        drivers = driver_service.get_all(include_deleted_users=include_deleted)

        return ErrorResponse.success(data=drivers)

    except Exception as e:
        logger.error(f"Failed to get all drivers: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Failed to get all drivers: {str(e)}')


@driver_api.route('/route/<int:route_id>', methods=['GET'])
def get_drivers_on_route(route_id):
    """
    Get all drivers assigned to buses on a specific route.

    Path Parameters:
        - route_id: int

    Returns:
        200: List of drivers with bus and route information
        500: Internal server error
    """
    try:
        driver_service = get_driver_service()
        drivers = driver_service.get_drivers_on_route(route_id)

        return ErrorResponse.success(data=drivers)

    except Exception as e:
        logger.error(f"Failed to get drivers on route: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Failed to get drivers on route: {str(e)}')


@driver_api.route('/check/<int:user_id>', methods=['GET'])
def check_is_driver(user_id):
    """
    Check if a user is a driver.

    Path Parameters:
        - user_id: int

    Returns:
        200: Boolean result
        500: Internal server error
    """
    try:
        driver_service = get_driver_service()
        is_driver = driver_service.is_user_driver(user_id)

        return ErrorResponse.success(data={'is_driver': is_driver})

    except Exception as e:
        logger.error(f"Failed to check if user is driver: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Failed to check driver status: {str(e)}')


@driver_api.route('/count', methods=['GET'])
def get_driver_count():
    """
    Get count of drivers by status.

    Query Parameters:
        - status: str (optional) - Active, Inactive, Suspended

    Returns:
        200: Driver count
        500: Internal server error
    """
    try:
        status = request.args.get('status')

        driver_service = get_driver_service()
        count = driver_service.get_driver_count(status)

        return ErrorResponse.success(data={'count': count})

    except Exception as e:
        logger.error(f"Failed to get driver count: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Failed to get driver count: {str(e)}')


@driver_api.route('/<int:driver_id>/status', methods=['PUT'])
@token_required
@admin_required
def update_driver_status(current_user, driver_id):
    """
    Update driver status (admin only).

    Path Parameters:
        - driver_id: int

    Request Body:
        - status: str (Active, Inactive, Suspended)

    Returns:
        200: Status updated successfully
        400: Validation error
        401: Unauthorized
        403: Forbidden
        404: Driver not found
        500: Internal server error
    """
    try:
        data = request.get_json()
        if not data or 'status' not in data:
            return ErrorResponse.fail("status is required")

        driver_service = get_driver_service()
        success = driver_service.update_status(driver_id, data['status'])

        if success:
            logger.info(f"Driver {driver_id} status updated by admin {current_user['id']}")
            return ErrorResponse.success(message='Driver status updated successfully')
        else:
            return ErrorResponse.fail('Failed to update driver status')

    except ValueError as e:
        logger.warning(f"Status update error: {str(e)}")
        return ErrorResponse.fail(str(e))
    except Exception as e:
        logger.error(f"Status update failed: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Status update failed: {str(e)}')


@driver_api.route('/<int:driver_id>/license', methods=['PUT'])
@token_required
@admin_required
def update_driver_license(current_user, driver_id):
    """
    Update driver's license number (admin only).

    Path Parameters:
        - driver_id: int

    Request Body:
        - license_number: str (min 5 characters)

    Returns:
        200: License updated successfully
        400: Validation error
        401: Unauthorized
        403: Forbidden
        404: Driver not found
        500: Internal server error
    """
    try:
        data = request.get_json()
        if not data or 'license_number' not in data:
            return ErrorResponse.fail("license_number is required")

        driver_service = get_driver_service()
        success = driver_service.update_license(driver_id, data['license_number'])

        if success:
            logger.info(f"Driver {driver_id} license updated by admin {current_user['id']}")
            return ErrorResponse.success(message='Driver license updated successfully')
        else:
            return ErrorResponse.fail('Failed to update driver license')

    except ValueError as e:
        logger.warning(f"License update error: {str(e)}")
        return ErrorResponse.fail(str(e))
    except Exception as e:
        logger.error(f"License update failed: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'License update failed: {str(e)}')


@driver_api.route('/<int:driver_id>/assign-bus', methods=['PUT'])
@token_required
@admin_required
def assign_driver_to_bus(current_user, driver_id):
    """
    Assign driver to a bus (admin only).

    Path Parameters:
        - driver_id: int

    Request Body:
        - bus_id: int

    Returns:
        200: Assignment successful
        400: Validation error
        401: Unauthorized
        403: Forbidden
        404: Driver not found
        500: Internal server error
    """
    try:
        data = request.get_json()
        if not data or 'bus_id' not in data:
            return ErrorResponse.fail("bus_id is required")

        driver_service = get_driver_service()
        success = driver_service.assign_to_bus(driver_id, data['bus_id'])

        if success:
            logger.info(f"Driver {driver_id} assigned to bus {data['bus_id']} by admin {current_user['id']}")
            return ErrorResponse.success(message='Driver assigned to bus successfully')
        else:
            return ErrorResponse.fail('Failed to assign driver to bus')

    except ValueError as e:
        logger.warning(f"Bus assignment error: {str(e)}")
        return ErrorResponse.fail(str(e))
    except Exception as e:
        logger.error(f"Bus assignment failed: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Bus assignment failed: {str(e)}')


@driver_api.route('/<int:driver_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_driver(current_user, driver_id):
    """
    Delete driver (admin only - hard delete).

    Path Parameters:
        - driver_id: int

    Returns:
        200: Driver deleted successfully
        401: Unauthorized
        403: Forbidden
        404: Driver not found
        500: Internal server error
    """
    try:
        driver_service = get_driver_service()
        success = driver_service.delete(driver_id)

        if success:
            logger.info(f"Driver {driver_id} deleted by admin {current_user['id']}")
            return ErrorResponse.success(message='Driver deleted successfully')
        else:
            return ErrorResponse.fail('Failed to delete driver')

    except ValueError as e:
        logger.warning(f"Driver deletion error: {str(e)}")
        return ErrorResponse.fail(str(e))
    except Exception as e:
        logger.error(f"Driver deletion failed: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Driver deletion failed: {str(e)}')
