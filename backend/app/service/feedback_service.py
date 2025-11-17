from datetime import datetime
from io import BytesIO
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from sqlalchemy import func
from sqlalchemy.orm import aliased

from app.main import db
from app.main.model.feedback import Feedback
from app.main.model.bus import Bus
from app.main.model.driver import Driver
from app.main.model.user import User
from flask import jsonify, send_file, request


def add(data,token):
    print(data)
    if token:
        auth_token = token.split(" ")[1]
        resp = User.decode_auth_token(auth_token)
        print(resp)
        user = User.query.filter_by(public_id=resp['uuid']).first()
        if not user:
            return jsonify({"status": "fail", "message": "Không tìm thấy người dùng."}), 404
        try:
            # Kiểm tra dữ liệu đầu vào
            feedback_content = data.get("content")
            bus_number = data.get("bus_id")

            if not feedback_content or not bus_number:
                return {
                    "status": "fail",
                    "message": "Dữ liệu không hợp lệ. 'feedback' và 'busNumber' là bắt buộc."
                }, 400

            # Tạo đối tượng feedback
            new_feedback = Feedback(
                bus_id=bus_number,
                content=feedback_content,
                user_id=user.id,
                status="pending",  # Mặc định trạng thái là 'new'
                created_at=datetime.now(),
                updated_at=datetime.now()
            )

            # Thêm vào cơ sở dữ liệu
            db.session.add(new_feedback)
            db.session.commit()

            return {
                "status": "success",
                "message": "Feedback đã được gửi thành công."
            }, 201

        except Exception as e:
            # Xử lý các lỗi khác
            db.session.rollback()  # Rollback nếu có lỗi
            return {
                "status": "fail",
                "message": f"Đã xảy ra lỗi khi gửi feedback: {str(e)}"
            }, 500

def get_all_feed(page,pageSize):
    try:
        # Tạo alias cho các bảng User để phân biệt giữa người gửi feedback và tài xế
        user_alias = aliased(User)
        driver_user_alias = aliased(User)

        # Tổng số feedbacks để tính toán phân trang
        total_count = db.session.query(func.count(Feedback.id)).scalar()
        feedbacks = (db.session.query(Feedback, Bus, user_alias,Driver,driver_user_alias).distinct().join(
            Bus, Bus.bus_id == Feedback.bus_id
        ).join(user_alias, user_alias.id == Feedback.user_id).join(
        Driver, Bus.bus_id== Driver.bus_id).join(
           driver_user_alias, driver_user_alias.id == Driver.user_id
        ).order_by(Feedback.created_at.desc()
        ).offset(
            (page-1)*pageSize
        ).limit(
            pageSize
        )
        .all())
        print(feedbacks)
        if not feedbacks:
            return jsonify({
                "status": "success",
                "message": "Không có feedback nào.",
                "data": [],
                "total_count": 0
            }), 200

        # Tạo danh sách feedbacks trả về
        feedback_list = []
        for feedback, bus, user, driver, driver_user in feedbacks:
            feedback_list.append({
                "feedback_id": feedback.id,
                "feedback_content": feedback.content,
                "feedback_status": feedback.status,
                "created_at": feedback.created_at,
                "bus_number": bus.plate_number,
                "bus_model": bus.model,
                "user_name": user.username,
                "driver_name": driver_user.username,
                "driver_phone": driver_user.phone,
            })

        return {
            "status": "success",
            "message": "Lấy danh sách feedback thành công.",
            "data": feedback_list,
            "total": total_count,  # Tổng số bản ghi
            "page": page,  # Trang hiện tại
            "page_size": pageSize  # Số bản ghi mỗi trang
        }, 200

    except Exception as e:
        return jsonify({
            "status": "fail",
            "message": f"Đã xảy ra lỗi khi lấy feedback: {str(e)}"
        }), 500
def generate_pdf_report(data):
    try:
        # Lấy dữ liệu từ reques
        start_date_str = data.get('startDate')
        end_date_str = data.get('endDate')
        # Kiểm tra nếu thiếu ngày bắt đầu hoặc ngày kết thúc
        if not start_date_str or not end_date_str:
            return jsonify({
                "status": "fail",
                "message": "Vui lòng cung cấp đầy đủ ngày bắt đầu và ngày kết thúc."
            }), 400

        # Chuyển đổi chuỗi ngày sang datetime
        start_date = datetime.fromisoformat(start_date_str)
        end_date = datetime.fromisoformat(end_date_str)

        # Truy vấn dữ liệu tổng số feedback đã gửi và tổng số người dùng
        total_feedbacks = db.session.query(Feedback).filter(
            Feedback.created_at >= start_date,
            Feedback.created_at <= end_date
        ).count()

        total_users = db.session.query(Feedback.user_id).filter(
            Feedback.created_at >= start_date,
            Feedback.created_at <= end_date
        ).distinct().count()

        # Truy vấn Top 3 xe và tài xế nhận nhiều feedback nhất
        top_buses_drivers = db.session.query(
            Bus.plate_number, Driver.user_id, db.func.count(Feedback.id).label('feedback_count')
        ).join(
            Feedback, Feedback.bus_id == Bus.bus_id
        ).join(
            Driver, Driver.bus_id == Bus.bus_id
        ).filter(
            Feedback.created_at >= start_date,
            Feedback.created_at <= end_date
        ).group_by(Bus.plate_number, Driver.user_id).order_by(db.func.count(Feedback.id).desc()).limit(3).all()

        # Truy vấn Top 3 người gửi feedback nhiều nhất
        top_users = db.session.query(
            User.username, db.func.count(Feedback.id).label('feedback_count')
        ).join(
            Feedback, Feedback.user_id == User.id
        ).filter(
            Feedback.created_at >= start_date,
            Feedback.created_at <= end_date
        ).group_by(User.username).order_by(db.func.count(Feedback.id).desc()).limit(3).all()

        # Tạo file PDF
        pdf_buffer = BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=letter)
        c.setFont("Helvetica", 12)

        # Title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(200, 750, "Feedback Report")

        # Tổng số feedback
        c.setFont("Helvetica", 12)
        c.drawString(50, 700, f"Total feedback sent: {total_feedbacks}")
        c.drawString(50, 685, f"Total user sent feedback: {total_users}")

        # Top 3 xe và tài xế nhận nhiều feedback
        c.drawString(50, 650, "Top 3 bus and driver receive most feedback:")
        y = 635
        for bus, driver_id, count in top_buses_drivers:
            driver_name = db.session.query(User.username).filter(User.id == driver_id).first()[0]
            c.drawString(50, y, f"Bus: {bus}, Driver: {driver_name} - Feedbacks: {count}")
            y -= 20

        # Top 3 người gửi feedback nhiều nhất
        c.drawString(50, y, "Top 3 user sent most feedbacks")
        y -= 20
        for user, count in top_users:
            c.drawString(50, y, f"User: {user} - Feedbacks: {count}")
            y -= 20

        # Lưu file PDF
        c.save()
        pdf_buffer.seek(0)
        # Xác định thư mục hiện tại của ứng dụng
        current_directory = os.path.dirname(os.path.abspath(__file__))

        # Xác định đường dẫn đến file PDF trong thư mục cùng với ứng dụng
        file_path = os.path.join(current_directory, 'report.pdf')
        with open(file_path, 'wb') as f:
            f.write(pdf_buffer.read())
        # Trả về file PDF
        pdf_buffer.seek(0)
        return send_file(pdf_buffer, as_attachment=True, download_name="feedback_report.pdf", mimetype="application/pdf")

    except Exception as e:
        # Xử lý lỗi và trả về thông báo lỗi
        return jsonify({
            "status": "fail",
            "message": f"Đã xảy ra lỗi khi tạo báo cáo: {str(e)}"
        }), 500
