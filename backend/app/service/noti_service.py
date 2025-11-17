from datetime import datetime

from app.main import db
from sqlalchemy import text

from app.main.model.noti import Notification
from app.main.model.user import User
from app.main.utils.dtov2 import NotiDTO


def get_list_noti(data):
    token = data.split(" ")[1]
    resp = User.decode_auth_token(token)
    if isinstance(resp, str):
        return {"message": resp}, 400
    user = User.query.filter_by(public_id=resp['uuid']).first()
    if user:
        noties = Notification.query.filter_by(user_id=user.id).all()
        return [NotiDTO.from_orm(noti).dict() for noti in noties]
def mark_read(id):
    try:
            # Kiểm tra thông báo tồn tại
        notification = Notification.query.get(id)
        if not notification:
            return {"message": "Notification not found"}, 404

            # Đánh dấu là đã đọc
        notification.read = True
        print(notification)
        notification.updated_at = datetime.utcnow()  # Cập nhật thời gian sửa đổi
        db.session.commit()

        return {"message": "Notification marked as read"}

    except Exception as e:
        db.session.rollback()  # Rollback nếu có lỗi
        print(f"Error: {e}")
        return {"message": "An error occurred"}, 500