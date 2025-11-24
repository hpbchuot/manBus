"""
Route and Stop Controllers - Handle route and stop-related HTTP endpoints.
Follows the same pattern as user_controller and auth_controller.
"""
from flask import request, Blueprint, jsonify, g
from pydantic import ValidationError
from app.middleware import token_required, admin_required
from app.middleware.error_handlers import ErrorResponse
import logging

logger = logging.getLogger(__name__)

# Create the Blueprints
route_api = Blueprint('route_api', __name__)
stop_api = Blueprint('stop_api', __name__)


def get_route_service():
    """Get route service from request context (request-scoped injection)."""
    if not hasattr(g, 'route_service'):
        from app.main import factory
        g.route_service = factory.get_route_service()
    return g.route_service


def get_stop_service():
    """Get stop service from request context (request-scoped injection)."""
    if not hasattr(g, 'stop_service'):
        from app.main import factory
        g.stop_service = factory.get_stop_service()
    return g.stop_service


# ============================================================================
# ROUTE ENDPOINTS
# ============================================================================

@route_api.route('/', methods=['POST'])
@token_required
@admin_required
def create_route(current_user):
    """
    Create a new route (admin operation).

    Request Body:
        - name: str (min 3 characters)
        - coordinates: JSONB array of [lat, lon] pairs

    Returns:
        201: Route created successfully
        400: Validation error
        401: Unauthorized
        403: Forbidden
        500: Internal server error
    """
    try:
        data = request.get_json()
        if not data:
            return ErrorResponse.fail("Request body is required")

        name = data.get('name')
        coordinates = data.get('coordinates')

        if not name or not coordinates:
            return ErrorResponse.fail("name and coordinates are required")

        route_service = get_route_service()
        route = route_service.create(name, coordinates)

        logger.info(f"Route created successfully: {route.get('id')}")
        return ErrorResponse.success(
            data=route,
            message='Route created successfully',
            status_code=201
        )

    except ValueError as e:
        logger.warning(f"Route creation error: {str(e)}")
        return ErrorResponse.fail(str(e))
    except Exception as e:
        logger.error(f"Route creation failed: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Route creation failed: {str(e)}')


@route_api.route('/<int:route_id>', methods=['GET'])
def get_route(route_id):
    """Get route by ID."""
    try:
        route_service = get_route_service()
        route = route_service.get_by_id(route_id)

        if not route:
            logger.warning(f"Route not found: {route_id}")
            return ErrorResponse.not_found('Route')

        return ErrorResponse.success(data=route)

    except Exception as e:
        logger.error(f"Failed to get route {route_id}: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Failed to get route: {str(e)}')


@route_api.route('/name/<string:route_name>', methods=['GET'])
def get_route_by_name(route_name):
    """Get route by name."""
    try:
        route_service = get_route_service()
        route = route_service.get_by_name(route_name)

        if not route:
            logger.warning(f"Route not found: {route_name}")
            return ErrorResponse.not_found('Route')

        return ErrorResponse.success(data=route)

    except Exception as e:
        logger.error(f"Failed to get route by name: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Failed to get route: {str(e)}')


@route_api.route('/', methods=['GET'])
def get_all_routes():
    """Get all routes with stop count and length."""
    try:
        route_service = get_route_service()
        routes = route_service.get_all()

        return ErrorResponse.success(data=routes)

    except Exception as e:
        logger.error(f"Failed to get all routes: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Failed to get all routes: {str(e)}')


@route_api.route('/<int:route_id>/stops', methods=['GET'])
def get_route_stops(route_id):
    """Get all stops for a route ordered by sequence."""
    try:
        route_service = get_route_service()
        stops = route_service.get_stops_on_route(route_id)

        return ErrorResponse.success(data=stops)

    except ValueError as e:
        logger.warning(f"Get route stops error: {str(e)}")
        return ErrorResponse.fail(str(e))
    except Exception as e:
        logger.error(f"Failed to get route stops: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Failed to get route stops: {str(e)}')


@route_api.route('/<int:route_id>/length', methods=['GET'])
def get_route_length(route_id):
    """Calculate route length in meters."""
    try:
        route_service = get_route_service()
        length = route_service.get_route_length(route_id)

        return ErrorResponse.success(data={'length': length})

    except ValueError as e:
        logger.warning(f"Get route length error: {str(e)}")
        return ErrorResponse.fail(str(e))
    except Exception as e:
        logger.error(f"Failed to get route length: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Failed to get route length: {str(e)}')


@route_api.route('/<int:route_id>/geojson', methods=['GET'])
def get_route_geojson(route_id):
    """Get route geometry as GeoJSON."""
    try:
        route_service = get_route_service()
        geojson = route_service.get_route_geojson(route_id)

        if not geojson:
            return ErrorResponse.fail('Route geometry not found')

        return ErrorResponse.success(data=geojson)

    except ValueError as e:
        logger.warning(f"Get route GeoJSON error: {str(e)}")
        return ErrorResponse.fail(str(e))
    except Exception as e:
        logger.error(f"Failed to get route GeoJSON: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Failed to get route GeoJSON: {str(e)}')


@route_api.route('/near', methods=['GET'])
def find_routes_near_location():
    """
    Find routes passing near a location.

    Query Parameters:
        - latitude: float
        - longitude: float
        - radius_meters: int (default: 500, max: 10000)

    Returns:
        200: List of routes with distance information
        400: Validation error
        500: Internal server error
    """
    try:
        latitude = request.args.get('latitude', type=float)
        longitude = request.args.get('longitude', type=float)
        radius_meters = request.args.get('radius_meters', 500, type=int)

        if latitude is None or longitude is None:
            return ErrorResponse.fail("latitude and longitude are required")

        route_service = get_route_service()
        routes = route_service.find_routes_near_location(latitude, longitude, radius_meters)

        return ErrorResponse.success(data=routes)

    except ValueError as e:
        logger.warning(f"Find routes near error: {str(e)}")
        return ErrorResponse.fail(str(e))
    except Exception as e:
        logger.error(f"Failed to find routes near location: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Failed to find routes: {str(e)}')


@route_api.route('/<int:route_id>/check-point', methods=['GET'])
def check_point_on_route(route_id):
    """
    Check if a point is within tolerance of a route.

    Query Parameters:
        - latitude: float
        - longitude: float
        - tolerance_meters: int (default: 100)

    Returns:
        200: Boolean result
        400: Validation error
        500: Internal server error
    """
    try:
        latitude = request.args.get('latitude', type=float)
        longitude = request.args.get('longitude', type=float)
        tolerance_meters = request.args.get('tolerance_meters', 100, type=int)

        if latitude is None or longitude is None:
            return ErrorResponse.fail("latitude and longitude are required")

        route_service = get_route_service()
        is_on_route = route_service.is_point_on_route(route_id, latitude, longitude, tolerance_meters)

        return ErrorResponse.success(data={'is_on_route': is_on_route})

    except ValueError as e:
        logger.warning(f"Check point on route error: {str(e)}")
        return ErrorResponse.fail(str(e))
    except Exception as e:
        logger.error(f"Failed to check point on route: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Failed to check point on route: {str(e)}')


@route_api.route('/<int:route_id>', methods=['PUT'])
@token_required
@admin_required
def update_route(current_user, route_id):
    """
    Update route information (admin only).

    Request Body:
        - name: str (optional, min 3 characters)
        - coordinates: JSONB array (optional)

    Returns:
        200: Route updated successfully
        400: Validation error
        401: Unauthorized
        403: Forbidden
        404: Route not found
        500: Internal server error
    """
    try:
        data = request.get_json()
        if not data:
            return ErrorResponse.fail("Request body is required")

        name = data.get('name')
        coordinates = data.get('coordinates')

        route_service = get_route_service()
        route = route_service.update(route_id, name, coordinates)

        logger.info(f"Route {route_id} updated by admin {current_user['id']}")
        return ErrorResponse.success(
            data=route,
            message='Route updated successfully'
        )

    except ValueError as e:
        logger.warning(f"Route update error: {str(e)}")
        return ErrorResponse.fail(str(e))
    except Exception as e:
        logger.error(f"Route update failed: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Route update failed: {str(e)}')


@route_api.route('/<int:route_id>/geometry', methods=['PUT'])
@token_required
@admin_required
def update_route_geometry(current_user, route_id):
    """Update route geometry (admin only)."""
    try:
        data = request.get_json()
        if not data or 'coordinates' not in data:
            return ErrorResponse.fail("coordinates is required")

        route_service = get_route_service()
        success = route_service.update_geometry(route_id, data['coordinates'])

        if success:
            logger.info(f"Route {route_id} geometry updated by admin {current_user['id']}")
            return ErrorResponse.success(message='Route geometry updated successfully')
        else:
            return ErrorResponse.fail('Failed to update route geometry')

    except ValueError as e:
        logger.warning(f"Geometry update error: {str(e)}")
        return ErrorResponse.fail(str(e))
    except Exception as e:
        logger.error(f"Geometry update failed: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Geometry update failed: {str(e)}')


@route_api.route('/<int:route_id>/stops/<int:stop_id>', methods=['POST'])
@token_required
@admin_required
def add_stop_to_route(current_user, route_id, stop_id):
    """Add a stop to a route (admin only)."""
    try:
        data = request.get_json() or {}
        sequence = data.get('sequence', 0)

        route_service = get_route_service()
        success = route_service.add_stop_to_route(route_id, stop_id, sequence)

        if success:
            logger.info(f"Stop {stop_id} added to route {route_id} by admin {current_user['id']}")
            return ErrorResponse.success(message='Stop added to route successfully')
        else:
            return ErrorResponse.fail('Failed to add stop to route')

    except ValueError as e:
        logger.warning(f"Add stop error: {str(e)}")
        return ErrorResponse.fail(str(e))
    except Exception as e:
        logger.error(f"Add stop failed: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Add stop failed: {str(e)}')


@route_api.route('/<int:route_id>/stops/<int:stop_id>', methods=['DELETE'])
@token_required
@admin_required
def remove_stop_from_route(current_user, route_id, stop_id):
    """Remove a stop from a route (admin only)."""
    try:
        route_service = get_route_service()
        success = route_service.remove_stop_from_route(route_id, stop_id)

        if success:
            logger.info(f"Stop {stop_id} removed from route {route_id} by admin {current_user['id']}")
            return ErrorResponse.success(message='Stop removed from route successfully')
        else:
            return ErrorResponse.fail('Failed to remove stop from route')

    except ValueError as e:
        logger.warning(f"Remove stop error: {str(e)}")
        return ErrorResponse.fail(str(e))
    except Exception as e:
        logger.error(f"Remove stop failed: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Remove stop failed: {str(e)}')


@route_api.route('/<int:route_id>/stops/reorder', methods=['PUT'])
@token_required
@admin_required
def reorder_route_stops(current_user, route_id):
    """
    Update stop sequences for a route (admin only).

    Request Body:
        - stop_sequences: JSONB array of {stop_id, sequence} objects

    Returns:
        200: Stops reordered successfully
        400: Validation error
        401: Unauthorized
        403: Forbidden
        500: Internal server error
    """
    try:
        data = request.get_json()
        if not data or 'stop_sequences' not in data:
            return ErrorResponse.fail("stop_sequences is required")

        route_service = get_route_service()
        success = route_service.reorder_route_stops(route_id, data['stop_sequences'])

        if success:
            logger.info(f"Route {route_id} stops reordered by admin {current_user['id']}")
            return ErrorResponse.success(message='Stops reordered successfully')
        else:
            return ErrorResponse.fail('Failed to reorder stops')

    except ValueError as e:
        logger.warning(f"Reorder stops error: {str(e)}")
        return ErrorResponse.fail(str(e))
    except Exception as e:
        logger.error(f"Reorder stops failed: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Reorder stops failed: {str(e)}')


@route_api.route('/<int:route_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_route(current_user, route_id):
    """Delete route (admin only - hard delete)."""
    try:
        route_service = get_route_service()
        success = route_service.delete(route_id)

        if success:
            logger.info(f"Route {route_id} deleted by admin {current_user['id']}")
            return ErrorResponse.success(message='Route deleted successfully')
        else:
            return ErrorResponse.fail('Failed to delete route')

    except ValueError as e:
        logger.warning(f"Route deletion error: {str(e)}")
        return ErrorResponse.fail(str(e))
    except Exception as e:
        logger.error(f"Route deletion failed: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Route deletion failed: {str(e)}')


# ============================================================================
# STOP ENDPOINTS
# ============================================================================

@stop_api.route('/', methods=['POST'])
@token_required
@admin_required
def create_stop(current_user):
    """
    Create a new stop (admin operation).

    Request Body:
        - name: str (min 3 characters)
        - latitude: float
        - longitude: float

    Returns:
        201: Stop created successfully
        400: Validation error
        401: Unauthorized
        403: Forbidden
        500: Internal server error
    """
    try:
        data = request.get_json()
        if not data:
            return ErrorResponse.fail("Request body is required")

        name = data.get('name')
        latitude = data.get('latitude')
        longitude = data.get('longitude')

        if not all([name, latitude is not None, longitude is not None]):
            return ErrorResponse.fail("name, latitude, and longitude are required")

        stop_service = get_stop_service()
        stop = stop_service.create(name, latitude, longitude)

        logger.info(f"Stop created successfully: {stop.get('id')}")
        return ErrorResponse.success(
            data=stop,
            message='Stop created successfully',
            status_code=201
        )

    except ValueError as e:
        logger.warning(f"Stop creation error: {str(e)}")
        return ErrorResponse.fail(str(e))
    except Exception as e:
        logger.error(f"Stop creation failed: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Stop creation failed: {str(e)}')


@stop_api.route('/<int:stop_id>', methods=['GET'])
def get_stop(stop_id):
    """Get stop by ID."""
    try:
        stop_service = get_stop_service()
        stop = stop_service.get_by_id(stop_id)

        if not stop:
            logger.warning(f"Stop not found: {stop_id}")
            return ErrorResponse.not_found('Stop')

        return ErrorResponse.success(data=stop)

    except Exception as e:
        logger.error(f"Failed to get stop {stop_id}: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Failed to get stop: {str(e)}')


@stop_api.route('/', methods=['GET'])
def get_all_stops():
    """Get all stops."""
    try:
        stop_service = get_stop_service()
        stops = stop_service.get_all()

        return ErrorResponse.success(data=stops)

    except Exception as e:
        logger.error(f"Failed to get all stops: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Failed to get all stops: {str(e)}')


@stop_api.route('/nearest', methods=['GET'])
def find_nearest_stops():
    """
    Find stops within a radius of a location.

    Query Parameters:
        - latitude: float
        - longitude: float
        - radius_meters: int (default: 1000)
        - limit: int (default: 10)

    Returns:
        200: List of stops with distance information
        400: Validation error
        500: Internal server error
    """
    try:
        latitude = request.args.get('latitude', type=float)
        longitude = request.args.get('longitude', type=float)
        radius_meters = request.args.get('radius_meters', 1000, type=int)
        limit = request.args.get('limit', 10, type=int)

        if latitude is None or longitude is None:
            return ErrorResponse.fail("latitude and longitude are required")

        route_service = get_route_service()
        stops = route_service.find_nearest_stops(latitude, longitude, radius_meters, limit)

        return ErrorResponse.success(data=stops)

    except ValueError as e:
        logger.warning(f"Find nearest stops error: {str(e)}")
        return ErrorResponse.fail(str(e))
    except Exception as e:
        logger.error(f"Failed to find nearest stops: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Failed to find nearest stops: {str(e)}')


@stop_api.route('/<int:stop_id>', methods=['PUT'])
@token_required
@admin_required
def update_stop(current_user, stop_id):
    """
    Update stop information (admin only).

    Request Body:
        - name: str (optional, min 3 characters)

    Returns:
        200: Stop updated successfully
        400: Validation error
        401: Unauthorized
        403: Forbidden
        404: Stop not found
        500: Internal server error
    """
    try:
        data = request.get_json()
        if not data:
            return ErrorResponse.fail("Request body is required")

        name = data.get('name')

        stop_service = get_stop_service()
        stop = stop_service.update(stop_id, name)

        logger.info(f"Stop {stop_id} updated by admin {current_user['id']}")
        return ErrorResponse.success(
            data=stop,
            message='Stop updated successfully'
        )

    except ValueError as e:
        logger.warning(f"Stop update error: {str(e)}")
        return ErrorResponse.fail(str(e))
    except Exception as e:
        logger.error(f"Stop update failed: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Stop update failed: {str(e)}')


@stop_api.route('/<int:stop_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_stop(current_user, stop_id):
    """Delete stop (admin only - hard delete)."""
    try:
        stop_service = get_stop_service()
        success = stop_service.delete(stop_id)

        if success:
            logger.info(f"Stop {stop_id} deleted by admin {current_user['id']}")
            return ErrorResponse.success(message='Stop deleted successfully')
        else:
            return ErrorResponse.fail('Failed to delete stop')

    except ValueError as e:
        logger.warning(f"Stop deletion error: {str(e)}")
        return ErrorResponse.fail(str(e))
    except Exception as e:
        logger.error(f"Stop deletion failed: {str(e)}", exc_info=True)
        return ErrorResponse.error(f'Stop deletion failed: {str(e)}')
