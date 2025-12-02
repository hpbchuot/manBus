"""
Bus Controller - Handles bus-related HTTP endpoints.
Follows the same pattern as user_controller and auth_controller.
"""
from flask import request, Blueprint, jsonify, g
from pydantic import ValidationError
from app.middleware import token_required, admin_required
from app.middleware.error_handlers import ErrorResponse
from app.schemas.bus_schemas import BusCreate, BusUpdate, BusLocationUpdate, BusStatusUpdate, BusRouteAssignment
import logging

logger = logging.getLogger(__name__)

# Create the Blueprint
bus_api = Blueprint('bus_api', __name__)


def get_bus_service():
    """
    Get bus service from request context (request-scoped injection).
    Follows DIP - dependency injected per request, not global coupling.
    """
    if not hasattr(g, 'bus_service'):
        from app.main import factory
        g.bus_service = factory.get_bus_service()
    return g.bus_service


@bus_api.route('/', methods=['POST'])
@token_required
@admin_required
def create_bus(current_user):
    """
    Create a new bus (admin operation).

    Request Body:
        - plate_number: str (unique)
        - name: str (optional)
        - model: str (optional)
        - status: str (optional, default: Active)
        - route_id: int

    Returns:
        201: Bus created successfully
        400: Validation error or duplicate plate number
        401: Unauthorized
        403: Forbidden
        500: Internal server error
    """
    try:
        data = request.get_json()
        if not data:
            return ErrorResponse.fail("Request body is required")

        bus_service = get_bus_service()

        # Validate and create bus using Pydantic schema
        bus_data = BusCreate(**data)
        bus = bus_service.create(bus_data)

        if not bus:
            return ErrorResponse.fail('Failed to create bus')

        logger.info(f"Bus created successfully: {bus.bus_id}")
        return ErrorResponse.success(
            data=bus.model_dump(),
            message='Bus created successfully',
            status_code=201
        )

    except ValidationError as e:
        logger.warning(f"Bus creation validation error: {e.errors()}")
        return ErrorResponse.validation_error(e)
    except ValueError as e:
        logger.warning(f"Bus creation business logic error: {str(e)}")
        return ErrorResponse.fail(str(e))
    except Exception as e:
        logger.error(f"Bus creation failed: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Bus creation failed: {str(e)}')


@bus_api.route('/by/<int:bus_id>', methods=['GET'])
def get_bus(bus_id):
    """
    Get bus by ID with route information.

    Path Parameters:
        - bus_id: int

    Returns:
        200: Bus data with route information
        404: Bus not found
        500: Internal server error
    """
    try:
        bus_service = get_bus_service()
        bus = bus_service.get_by_id(bus_id)

        if not bus:
            logger.warning(f"Bus not found: {bus_id}")
            return ErrorResponse.not_found('Bus')

        return ErrorResponse.success(data=bus.model_dump())

    except Exception as e:
        logger.error(f"Failed to get bus {bus_id}: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Failed to get bus by id: {str(e)}')


@bus_api.route('/plate/<string:plate_number>', methods=['GET'])
def get_bus_by_plate(plate_number):
    """
    Get bus by plate number.

    Path Parameters:
        - plate_number: str

    Returns:
        200: Bus data
        404: Bus not found
        500: Internal server error
    """
    try:
        bus_service = get_bus_service()
        bus = bus_service.get_by_plate_number(plate_number)

        if not bus:
            logger.warning(f"Bus not found with plate: {plate_number}")
            return ErrorResponse.not_found('Bus')

        return ErrorResponse.success(data=bus.model_dump())

    except Exception as e:
        logger.error(f"Failed to get bus by plate: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Failed to get bus by plate: {str(e)}')


@bus_api.route('/active', methods=['GET'])
def get_active_buses():
    """
    Get all active buses.

    Returns:
        200: List of active buses
        500: Internal server error
    """
    try:
        bus_service = get_bus_service()
        cursor = request.args.get('cursor', type=int) or None
        limit = request.args.get('limit', 10, type=int)
        buses = bus_service.get_all_active(cursor, limit+1)

        has_next = len(buses) > limit
        next_cursor = buses[-1].bus_id if has_next else None
        return ErrorResponse.success(
            data={
                'buses': [bus.model_dump() for bus in buses[:-1]] if has_next else [bus.model_dump() for bus in buses],
                'next_cursor': next_cursor,
                'has_next': has_next
            }
        )

    except Exception as e:
        logger.error(f"Failed to get active buses: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Failed to get active buses: {str(e)}')


@bus_api.route('/', methods=['GET'])
def get_all_buses():
    """
    Get all buses.

    Query Parameters:
        - include_inactive: bool (default: false)

    Returns:
        200: List of buses
        500: Internal server error
    """
    try:
        cursor = request.args.get('cursor', type=int) or None
        limit = request.args.get('limit', 10, type=int)
        include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'

        bus_service = get_bus_service()
        buses = bus_service.get_all(cursor, limit+1, include_inactive)
        has_next = len(buses) > limit
        next_cursor = buses[-1].bus_id if has_next else None
        return ErrorResponse.success(
            data={
                'buses': [bus.model_dump() for bus in buses[:-1]] if has_next else [bus.model_dump() for bus in buses],
                'next_cursor': next_cursor,
                'has_next': has_next
            }
        )

    except Exception as e:
        logger.error(f"Failed to get all buses: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Failed to get all buses: {str(e)}')


@bus_api.route('/route/<int:route_id>', methods=['GET'])
def get_buses_by_route(route_id):
    """
    Get all buses on a specific route.

    Path Parameters:
        - route_id: int

    Returns:
        200: List of buses on the route
        500: Internal server error
    """
    try:
        bus_service = get_bus_service()
        buses = bus_service.get_buses_by_route(route_id)

        return ErrorResponse.success(data=[bus.model_dump() for bus in buses])

    except Exception as e:
        logger.error(f"Failed to get buses by route: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Failed to get buses by route: {str(e)}')


@bus_api.route('/nearest', methods=['GET'])
def find_nearest_buses():
    """
    Find nearest buses to a location.

    Query Parameters:
        - latitude: float
        - longitude: float
        - route_id: int (optional)
        - limit: int (default: 5)

    Returns:
        200: List of nearest buses with distance
        400: Validation error
        500: Internal server error
    """
    try:
        latitude = request.args.get('latitude', type=float)
        longitude = request.args.get('longitude', type=float)
        route_id = request.args.get('route_id', type=int)
        limit = request.args.get('limit', 5, type=int)

        if latitude is None or longitude is None:
            return ErrorResponse.fail("latitude and longitude are required")

        bus_service = get_bus_service()
        buses = bus_service.find_nearest_buses(latitude, longitude, route_id, limit)

        return ErrorResponse.success(data=buses)

    except Exception as e:
        logger.error(f"Failed to find nearest buses: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Failed to find nearest buses: {str(e)}')


@bus_api.route('/count/active', methods=['GET'])
def get_active_buses_count():
    """
    Get count of active buses.

    Returns:
        200: Active bus count
        500: Internal server error
    """
    try:
        bus_service = get_bus_service()
        count = bus_service.get_active_buses_count()

        return ErrorResponse.success(data={'count': count})

    except Exception as e:
        logger.error(f"Failed to get active bus count: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Failed to get active bus count: {str(e)}')


@bus_api.route('/<int:bus_id>', methods=['PUT'])
@token_required
@admin_required
def update_bus(current_user, bus_id):
    """
    Update bus information (admin only).

    Path Parameters:
        - bus_id: int

    Request Body:
        - plate_number: str (optional)
        - name: str (optional)
        - model: str (optional)
        - status: str (optional)
        - route_id: int (optional)

    Returns:
        200: Bus updated successfully
        400: Validation error
        401: Unauthorized
        403: Forbidden
        404: Bus not found
        500: Internal server error
    """
    try:
        data = request.get_json()
        if not data:
            return ErrorResponse.fail("Request body is required")

        bus_service = get_bus_service()

        # Validate and update using Pydantic schema
        bus_data = BusUpdate(**data)
        bus = bus_service.update(bus_id, bus_data)

        if not bus:
            logger.warning(f"Bus not found for update: {bus_id}")
            return ErrorResponse.not_found('Bus')

        logger.info(f"Bus updated successfully: {bus_id} by admin {current_user['id']}")
        return ErrorResponse.success(
            data=bus.model_dump(),
            message='Bus updated successfully'
        )

    except ValidationError as e:
        logger.warning(f"Bus update validation error: {e.errors()}")
        return ErrorResponse.validation_error(e)
    except ValueError as e:
        logger.warning(f"Bus update business logic error: {str(e)}")
        return ErrorResponse.fail(str(e))
    except Exception as e:
        logger.error(f"Bus update failed: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Bus update failed: {str(e)}')


@bus_api.route('/<int:bus_id>/status', methods=['PUT'])
@token_required
@admin_required
def update_bus_status(current_user, bus_id):
    """
    Update bus status (admin only).

    Path Parameters:
        - bus_id: int

    Request Body:
        - status: str (Active, Inactive, Maintenance, Retired)

    Returns:
        200: Status updated successfully
        400: Validation error
        401: Unauthorized
        403: Forbidden
        404: Bus not found
        500: Internal server error
    """
    try:
        data = request.get_json()
        if not data:
            return ErrorResponse.fail("Request body is required")

        bus_service = get_bus_service()

        # Validate using Pydantic schema
        status_data = BusStatusUpdate(**data)
        success = bus_service.update_status(bus_id, status_data)

        if success:
            logger.info(f"Bus {bus_id} status updated by admin {current_user['id']}")
            return ErrorResponse.success(message='Bus status updated successfully')
        else:
            return ErrorResponse.fail('Failed to update bus status')

    except ValidationError as e:
        logger.warning(f"Status update validation error: {e.errors()}")
        return ErrorResponse.validation_error(e)
    except ValueError as e:
        logger.warning(f"Status update error: {str(e)}")
        return ErrorResponse.fail(str(e))
    except Exception as e:
        logger.error(f"Status update failed: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Status update failed: {str(e)}')


@bus_api.route('/<int:bus_id>/location', methods=['PUT'])
@token_required
def update_bus_location(current_user, bus_id):
    """
    Update bus location (real-time tracking).
    Can be called by drivers or admin.

    Path Parameters:
        - bus_id: int

    Request Body:
        - location: object with latitude and longitude

    Returns:
        200: Location updated successfully
        400: Validation error
        401: Unauthorized
        404: Bus not found
        500: Internal server error
    """
    try:
        data = request.get_json()
        if not data:
            return ErrorResponse.fail("Request body is required")

        bus_service = get_bus_service()

        # Validate using Pydantic schema
        location_data = BusLocationUpdate(**data)
        success = bus_service.update_location(bus_id, location_data)

        if success:
            logger.info(f"Bus {bus_id} location updated by user {current_user['id']}")
            return ErrorResponse.success(message='Bus location updated successfully')
        else:
            return ErrorResponse.fail('Failed to update bus location')

    except ValidationError as e:
        logger.warning(f"Location update validation error: {e.errors()}")
        return ErrorResponse.validation_error(e)
    except ValueError as e:
        logger.warning(f"Location update error: {str(e)}")
        return ErrorResponse.fail(str(e))
    except Exception as e:
        logger.error(f"Location update failed: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Location update failed: {str(e)}')


@bus_api.route('/<int:bus_id>/assign-route', methods=['PUT'])
@token_required
@admin_required
def assign_bus_to_route(current_user, bus_id):
    """
    Assign bus to a route (admin only).

    Path Parameters:
        - bus_id: int

    Request Body:
        - route_id: int

    Returns:
        200: Assignment successful
        400: Validation error
        401: Unauthorized
        403: Forbidden
        404: Bus not found
        500: Internal server error
    """
    try:
        data = request.get_json()
        if not data:
            return ErrorResponse.fail("Request body is required")

        bus_service = get_bus_service()

        # Validate using Pydantic schema
        assignment = BusRouteAssignment(**data)
        success = bus_service.assign_to_route(bus_id, assignment)

        if success:
            logger.info(f"Bus {bus_id} assigned to route {assignment.route_id} by admin {current_user['id']}")
            return ErrorResponse.success(message='Bus assigned to route successfully')
        else:
            return ErrorResponse.fail('Failed to assign bus to route')

    except ValidationError as e:
        logger.warning(f"Route assignment validation error: {e.errors()}")
        return ErrorResponse.validation_error(e)
    except ValueError as e:
        logger.warning(f"Route assignment error: {str(e)}")
        return ErrorResponse.fail(str(e))
    except Exception as e:
        logger.error(f"Route assignment failed: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Route assignment failed: {str(e)}')


@bus_api.route('/<int:bus_id>/on-route', methods=['GET'])
def check_bus_on_route(bus_id):
    """
    Check if bus is on its assigned route.

    Path Parameters:
        - bus_id: int

    Query Parameters:
        - tolerance_meters: int (default: 100)

    Returns:
        200: Boolean result
        400: Validation error
        404: Bus not found
        500: Internal server error
    """
    try:
        tolerance_meters = request.args.get('tolerance_meters', 100, type=int)

        bus_service = get_bus_service()
        is_on_route = bus_service.is_bus_on_route(bus_id, tolerance_meters)

        return ErrorResponse.success(data={'is_on_route': is_on_route})

    except ValueError as e:
        logger.warning(f"Check bus on route error: {str(e)}")
        return ErrorResponse.fail(str(e))
    except Exception as e:
        logger.error(f"Failed to check bus on route: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Failed to check bus on route: {str(e)}')


@bus_api.route('/<int:bus_id>/location-details', methods=['GET'])
def get_bus_location_details(bus_id):
    """
    Get detailed location information for a bus.

    Path Parameters:
        - bus_id: int

    Returns:
        200: Location details
        404: Bus not found
        500: Internal server error
    """
    try:
        bus_service = get_bus_service()
        location_details = bus_service.get_bus_location_details(bus_id)

        if not location_details:
            logger.warning(f"Bus location details not found: {bus_id}")
            return ErrorResponse.not_found('Bus location details')

        return ErrorResponse.success(data=location_details)

    except ValueError as e:
        logger.warning(f"Get location details error: {str(e)}")
        return ErrorResponse.fail(str(e))
    except Exception as e:
        logger.error(f"Failed to get bus location details: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Failed to get bus location details: {str(e)}')


@bus_api.route('/<int:bus_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_bus(current_user, bus_id):
    """
    Delete bus (admin only).

    Path Parameters:
        - bus_id: int

    Returns:
        200: Bus deleted successfully
        401: Unauthorized
        403: Forbidden
        404: Bus not found
        500: Internal server error
    """
    try:
        bus_service = get_bus_service()
        success = bus_service.delete(bus_id)

        if success:
            logger.info(f"Bus {bus_id} deleted by admin {current_user['id']}")
            return ErrorResponse.success(message='Bus deleted successfully')
        else:
            return ErrorResponse.fail('Failed to delete bus')

    except ValueError as e:
        logger.warning(f"Bus deletion error: {str(e)}")
        return ErrorResponse.fail(str(e))
    except Exception as e:
        logger.error(f"Bus deletion failed: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Bus deletion failed: {str(e)}')
