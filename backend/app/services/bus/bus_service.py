from flask_migrate import current

from app.main import db
from sqlalchemy import text
from sqlalchemy.orm import joinedload

#from app.main.controller.manager_controller import driver
from app.main.model.bus import Bus
from sqlalchemy import text

from app.main.model.driver import Driver
from app.main.model.user import User
from app.main.utils.dtov2 import BusDTO


def get_st_end(bus_id):
    # Lấy đối tượng bus_road từ cơ sở dữ liệu
    bus_road = (
        Bus.query
        .filter(Bus.bus_id == bus_id)
        .options(joinedload(Bus.road))  # Giả sử bạn đang tải đối tượng `road` liên quan
        .first()
    )

    if not bus_road or not bus_road.road.route_geom:
        return {"message": "Không tìm thấy đường đi hoặc dữ liệu không hợp lệ."}, 400

    # Truy vấn lấy tọa độ điểm đầu và điểm cuối từ `route_geom`
    point_query = text("""
        SELECT ST_AsText(ST_StartPoint(route_geom)) AS start_point,
               ST_AsText(ST_EndPoint(route_geom)) AS end_point
        FROM road
        WHERE id = :route_id
    """)

    result = db.session.execute(point_query, {'route_id': bus_road.road.id})
    points = result.fetchone()

    if points:
        # Truy cập các phần tử trong tuple thông qua chỉ mục
        start_point = points[0]  # Chỉ mục 0 là start_point
        end_point = points[1]  # Chỉ mục 1 là end_point

        # Chuyển đổi tọa độ từ WKT (Well-Known Text) thành (lat, lng)
        start_point = start_point.replace('POINT(', '').replace(')', '')
        end_point = end_point.replace('POINT(', '').replace(')', '')

        start_lng, start_lat = map(float, start_point.split(' '))
        end_lng, end_lat = map(float, end_point.split(' '))

        # Trả về cặp tọa độ dưới dạng object
        return {
            "start": {"lat": start_lat, "lng": start_lng},
            "end": {"lat": end_lat, "lng": end_lng}
        }, 200

    return {"message": "Không thể lấy tọa độ của tuyến xe."}, 500
def get_all_bus():
    buses = Bus.query.filter_by(status='active').all()  # Lấy danh sách các xe bus với trạng thái 'active'
    return [BusDTO.from_orm(bus).dict() for bus in buses]
def get_bus(data):
    token = data.split(" ")[1]
    resp = User.decode_auth_token(token)
    if isinstance(resp, str):
        return {"message":resp},400
    user = User.query.filter_by(public_id=resp['uuid']).first()
    if user:
        driver = Driver.query.filter_by(user_id=user.id).first()
        result = {
            "user": {
                "id": user.id,
                "public_id": user.public_id,
                "uname": user.username,
                "name":user.name
            },
            "driver": {
                "id": driver.id,
                "license_number": driver.license_number,
            },
            "bus":
                {
                    "id": driver.bus.bus_id,
                    "license_plate": driver.bus.plate_number,
                }
        }

        return result, 200

    return {"message":"not found"},400
