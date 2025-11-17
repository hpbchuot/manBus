import uuid
import datetime

from flask_restx.inputs import email
from sqlalchemy import or_
from sqlalchemy.orm import joinedload

from app.main import db
from app.main.model.driver import Driver
from app.main.model.user import User
from app.main.utils.dtov2 import ManDTO, UserList


def to_pascal_case(name):
    # Tách chuỗi thành các từ, viết hoa chữ cái đầu của mỗi từ, sau đó nối lại với nhau
    return ' '.join(word.capitalize() for word in name.split())

def create(data):
    user = User.query.filter(
        or_(
            User.email == data.email,
            User.phone == data.phone,
            User.username == data.username
        )
    ).first()
    if not user:
        pascal_case_name = to_pascal_case(data.name)
        new_user = User(
            public_id=str(uuid.uuid4()),
            email=data.email,
            name = pascal_case_name,
            phone=data.phone,
            admin=False,
            role = 2,
            username=data.username,
            password=data.password,
            registered_on=datetime.datetime.utcnow()
        )
        save_changes(new_user)
        response_object = {
            'status': 'success',
            'message': 'Successfully registered.',
        }
        return response_object, 201
    else:
        response_object = {
            'status': 'fail',
            'message': 'User already exists. Try again.',
        }
        return response_object, 409


def create_driver(data):
    # Kiểm tra xem User đã tồn tại dựa trên email, phone, hoặc username
    user = User.query.filter(
        or_(
            User.email == data["email"],
            User.phone == data["phone"],
            User.username == data["username"],
        )
    ).first()

    tx = Driver.query.filter_by(license_number=data["blx"]).first()
    if user:
        return {
            "status": "fail",
            "message": "User already exists. Use another info to create a driver account.",
        }, 409
    if tx:
        return {
            "status": "fail",
            "message": "Thông tin tài xế đã tồn tại.",
        }, 409

    # Nếu cả user và tx chưa tồn tại, tạo mới
    pascal_case_name = to_pascal_case(data["name"])
    new_user = User(
        public_id=str(uuid.uuid4()),
        email=data["email"],
        name=pascal_case_name,
        phone=data["phone"],
        admin=False,
        role=4,
        username=data["username"],
        password=data["password"],
        registered_on=datetime.datetime.utcnow(),
    )
    save_changes(new_user)

    try:
        # Tạo Driver
        new_driver = Driver(
            license_number=data["blx"],
            bus_id=data["bus_id"],
            status="active",
            user_id=new_user.id,
        )
        save_changes(new_driver)
    except Exception as e:
        # Nếu lỗi xảy ra khi thêm driver, rollback user đã thêm trước đó
        db.session.rollback()  # Đảm bảo hủy tất cả các thay đổi trong phiên
        User.query.filter_by(id=new_user.id).delete()  # Xóa User vừa thêm
        db.session.commit()
        return {
            "status": "fail",
            "message": "Lỗi khi thêm tài xế, vui lòng thử lại",
        }, 500

    return {
        "status": "success",
        "message": "Đăng kí tài xế thành công.",
    }, 201

def update_driver(data):
    driver = (
        Driver.query
        .filter(Driver.status == 'active',
                Driver.license_number == data['blx'])  # Filter by active status and license number
        .options(joinedload(Driver.user))  # Load related User data along with Driver
        .first()  # Use first() to get a single result instead of a list
    )
    if not driver:
        return ({'error': 'Có lỗi xảy ra khi tìm tài xế'}), 404
    # Kiểm tra trùng lặp email hoặc phone với user khác
    print('driver',driver)
    existing_user = User.query.filter(
        or_(
            User.email == data["email"],
            User.phone == data["phone"]
        ),
        User.id != driver.user.id  # Tránh kiểm tra chính tài xế này
    ).first()
    if existing_user:
        return {
            "status": "fail",
            "message": "Email hoặc số điện thoại đã được sử dụng bởi tài khoản khác.",
        }, 409

    # không check bus id mà thêm luôn, lỗi -> do bus_id ko ton tai
    driver.user.email = data['email']
    driver.user.phone = data['phone']
    driver.bus_id = data['bus_id']
    try:
        db.session.commit()  # All changes are saved when commit() is called
        return {
            "status": "success",
            "message": "Cập nhật thông tin tài xế thành công.",
        }, 200
    except Exception as e:
        # In case of error, rollback the changes
        db.session.rollback()
        return {
            "status": "fail",
            "message": f"Cập nhật thất bại.",
        }, 500

def update_manager():
    return

def get_all_manager():
    managers = User.query.filter_by(isDeleted=False,role = 2).all()
    return [ManDTO.from_orm(manager).dict() for manager in managers]
# def get_all_user():
#     users = User.query.filter_by(isDeleted=False,role = 1).all()
#     return [UserList.from_orm(user).dict() for user in users]
def get_all_user(page, pageSize):
    # Lấy tổng số user
    total = User.query.filter_by(isDeleted=False, role=1).count()
    users = (User.query.filter_by(isDeleted=False, role=1)
             .offset((page - 1) * pageSize)
             .limit(pageSize)
             .all())
    return {
        'data': [UserList.from_orm(user).dict() for user in users],
        'total': total
    }
def delete_user(data):
    try:
        email = data['email']
        user = User.query.filter_by(email=email).first()
        if not user:
            return ({'error': 'User not found'}), 404
        user.isDeleted = True
        # Lưu thay đổi vào cơ sở dữ liệu
        db.session.commit()
        return ({'message': 'Xóa người dùng thành công'}), 200

    except Exception as e:
        db.session.rollback()
        raise e  # Hoặc ghi log lỗi
def delete_tai_xe(data):
    try:
        email = data['email']
        user = User.query.filter_by(email=email).first()
        if user:
            tx = Driver.query.filter_by(user_id=user.id).first()
            if tx:
                tx.status = 'deleted'
                user.isDeleted = True
                # Lưu thay đổi vào cơ sở dữ liệu
                db.session.commit()
                return ({'message': 'Xóa tài xế thành công'}), 200
            else:
                return ({'error': 'Driver not found'}), 404
        if not user:
            return ({'error': 'User not found'}), 404
    except Exception as e:
        db.session.rollback()
        raise e  # Hoặc ghi log lỗi
def get_all_driver(page,pageSize):
    # Lấy tất cả các driver và thông tin user tương ứng
    total = Driver.query.filter(Driver.status == 'active').count()
    drivers = (
        Driver.query
        .filter(Driver.status == 'active')
        .offset((page - 1) * pageSize)
        .limit(pageSize)
        .options(joinedload(Driver.user))  # Sau đó nạp dữ liệu liên quan
        .all()
    )

    # Chuyển dữ liệu thành dạng dictionary phẳng
    result = []
    for driver in drivers:
        result.append({
            "driver_id": driver.id,
            "blx": driver.license_number,
            "status": driver.status,
            "bus_id": driver.bus_id,
            "user_id": driver.user.id,
            "name": driver.user.name,
            "email": driver.user.email,
            "phone": driver.user.phone,
            "username": driver.user.username,
        })

    return {
        "data":result,
        "total":total
    }

def save_changes(data):
    try:
        db.session.add(data)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e  # Hoặc ghi log lỗi