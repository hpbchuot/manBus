"""
Bus Service - Refactored to follow Single Responsibility Principle

This service now focuses ONLY on bus-related business logic.
Authentication and token parsing are handled at the middleware/controller level.
Data access is delegated to repositories.
"""
from app.main import db
from sqlalchemy import text
from sqlalchemy.orm import joinedload
from app.main.model.bus import Bus
from app.main.model.driver import Driver
from app.main.utils.dtov2 import BusDTO


class BusService:
    """Service for bus-related business logic only"""

    def __init__(self, bus_repository=None, driver_repository=None):
        """
        Initialize with optional repositories (DIP)
        Falls back to direct ORM if repositories not provided (backward compatibility)
        """
        self._bus_repo = bus_repository
        self._driver_repo = driver_repository

    def get_route_endpoints(self, bus_id):
        """
        Get start and end coordinates of a bus route

        Args:
            bus_id: The bus ID

        Returns:
            dict: Start and end coordinates with lat/lng
        """
        # Get bus with route data
        bus_road = (
            Bus.query
            .filter(Bus.bus_id == bus_id)
            .options(joinedload(Bus.road))
            .first()
        )

        if not bus_road or not bus_road.road.route_geom:
            raise ValueError("Không tìm thấy đường đi hoặc dữ liệu không hợp lệ.")

        # Query for route geometry endpoints
        point_query = text("""
            SELECT ST_AsText(ST_StartPoint(route_geom)) AS start_point,
                   ST_AsText(ST_EndPoint(route_geom)) AS end_point
            FROM road
            WHERE id = :route_id
        """)

        result = db.session.execute(point_query, {'route_id': bus_road.road.id})
        points = result.fetchone()

        if not points:
            raise ValueError("Không thể lấy tọa độ của tuyến xe.")

        # Parse WKT coordinates
        start_point = points[0].replace('POINT(', '').replace(')', '')
        end_point = points[1].replace('POINT(', '').replace(')', '')

        start_lng, start_lat = map(float, start_point.split(' '))
        end_lng, end_lat = map(float, end_point.split(' '))

        return {
            "start": {"lat": start_lat, "lng": start_lng},
            "end": {"lat": end_lat, "lng": end_lng}
        }

    def get_all_active_buses(self):
        """
        Get all active buses

        Returns:
            list: List of bus DTOs
        """
        buses = Bus.query.filter_by(status='active').all()
        return [BusDTO.from_orm(bus).dict() for bus in buses]

    def get_bus_by_user(self, user_id):
        """
        Get bus information for a specific user
        NOTE: Token parsing removed - should be handled by middleware/controller

        Args:
            user_id: The user's ID (not public_id, actual database ID)

        Returns:
            dict: Bus, driver, and user information
        """
        from app.main.model.user import User

        # Get user
        user = User.query.get(user_id)
        if not user:
            raise ValueError("User not found")

        # Get driver for this user
        driver = Driver.query.filter_by(user_id=user.id).first()
        if not driver:
            raise ValueError("Driver not found for this user")

        if not driver.bus:
            raise ValueError("No bus assigned to this driver")

        # Return structured data
        return {
            "user": {
                "id": user.id,
                "public_id": user.public_id,
                "uname": user.username,
                "name": user.name
            },
            "driver": {
                "id": driver.id,
                "license_number": driver.license_number,
            },
            "bus": {
                "id": driver.bus.bus_id,
                "license_plate": driver.bus.plate_number,
            }
        }


# Backward compatibility - maintain old function signatures
def get_st_end(bus_id):
    """Legacy function - delegates to BusService"""
    service = BusService()
    try:
        return service.get_route_endpoints(bus_id), 200
    except ValueError as e:
        return {"message": str(e)}, 400
    except Exception:
        return {"message": "Không thể lấy tọa độ của tuyến xe."}, 500


def get_all_bus():
    """Legacy function - delegates to BusService"""
    service = BusService()
    return service.get_all_active_buses()


def get_bus(data):
    """
    Legacy function - DEPRECATED
    WARNING: This function violates SRP by mixing token parsing with business logic
    Use BusService.get_bus_by_user() instead and handle authentication at controller level
    """
    from app.main.model.user import User

    # Parse token (SRP violation - should be in middleware)
    token = data.split(" ")[1]
    resp = User.decode_auth_token(token)
    if isinstance(resp, str):
        return {"message": resp}, 400

    # Get user by token
    user = User.query.filter_by(public_id=resp['uuid']).first()
    if not user:
        return {"message": "not found"}, 400

    # Delegate to service
    service = BusService()
    try:
        return service.get_bus_by_user(user.id), 200
    except ValueError as e:
        return {"message": str(e)}, 400
