from flask_migrate import current
from app.main import db
from app.main.model.blacklist import BlacklistToken
from sqlalchemy import text

from app.main.model.map import BusRoute


def get_location(data):
    print(data)
    road = BusRoute.query.filter_by(id=data['id']).first()

    # Lấy số lượng điểm trong route_geom
    num_points_query = text("""
        SELECT ST_NumPoints(route_geom) 
        FROM road
        WHERE id = :route_id
    """)

    result = db.session.execute(num_points_query, {'route_id': data['id']})
    num_points = result.scalar()

    if num_points is None or num_points <= 1:
        print("Route has insufficient points to calculate segment location.")
        return

    point_query = text("""
        SELECT ST_AsText(ST_PointN(route_geom, :current_segment))
        FROM road
        WHERE id = :route_id
    """)

    result = db.session.execute(point_query, {'current_segment': road.current_segment, 'route_id': data['id']})
    point_location = result.scalar()

    # In ra tọa độ và số thứ tự của điểm
    print("Point Location:", point_location)
    print("Current Segment:", road.current_segment)
    if point_location:
        location_str = point_location.replace('POINT(', '').replace(')', '')
        lng, lat = map(float, location_str.split(' '))

        print(f"Location of Segment {road.current_segment}: Latitude = {lat}, Longitude = {lng}")
        return {"lng": lng, "lat": lat},200
    else:
        return {
            "message": "Có lỗi khi lấy dữ liệu",
        }, 500

