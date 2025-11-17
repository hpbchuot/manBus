from flask_restx import Namespace, fields


class UserDto:
    api = Namespace('user', description='user related operations')
    user = api.model('user', {
        'email': fields.String(required=True, description='user email address'),
        'username': fields.String(required=True, description='user username'),
        'password': fields.String(required=True, description='user password'),
        'public_id': fields.String(description='user Identifier')
    })
    user_register = api.model('UserRegisterDTO', {
        'fname': fields.String(required=True, description='First name of the user'),
        'lname': fields.String(required=True, description='Last name of the user'),
        'username': fields.String(required=True, description='Username for the user'),
        'email': fields.String(required=True, description='Email address of the user'),
        'phone': fields.String(required=True, description='Phone number of the user'),
        'password': fields.String(required=True, description='Password for the user')
    })
    man_register = api.model('ManagerRegisterDTO', {
        'name': fields.String(required=True, description='First name of the user'),
        'username': fields.String(required=True, description='Username for the user'),
        'email': fields.String(required=True, description='Email address of the user'),
        'phone': fields.String(required=True, description='Phone number of the user'),
        'password': fields.String(required=True, description='Password for the user')
    })

class AuthDto:
    api = Namespace('auth', description='authentication related operations')
    user_auth = api.model('auth_details', {
        'email': fields.String(required=True, description='The email address'),
        'password': fields.String(required=True, description='The user password '),
    })
class ManDto:
    api = Namespace('manager', description='feature for manager')
    man_register = api.model('ManagerRegisterDTO', {
        'name': fields.String(required=True, description='First name of the user'),
        'username': fields.String(required=True, description='Username for the user'),
        'email': fields.String(required=True, description='Email address of the user'),
        'phone': fields.String(required=True, description='Phone number of the user'),
        'password': fields.String(required=True, description='Password for the user')
    })
    manager = api.model('Manager', {
        'name': fields.String(required=True, description='First name of the user'),
        'username': fields.String(required=True, description='Username for the user'),
        'email': fields.String(required=True, description='Email address of the user'),
        'phone': fields.String(required=True, description='Phone number of the user')
    })
    driver_register = api.model('ManagerRegisterDTO', {
        'name': fields.String(required=True, description='First name of the user'),
        'username': fields.String(required=True, description='Username for the user'),
        'email': fields.String(required=True, description='Email address of the user'),
        'phone': fields.String(required=True, description='Phone number of the user'),
        'password': fields.String(required=True, description='Password for the user'),
        'blx':fields.String(required=True, description='thong tin bang lai xe'),
        'bus_id':fields.Integer(required=True, description='bus id ref to bus Table'),
    })
    driver_update = api.model('ManagerRegisterDTO', {
        'name': fields.String(required=True, description='First name of the user'),
        'username': fields.String(required=True, description='Username for the user'),
        'email': fields.String(required=True, description='Email address of the user'),
        'phone': fields.String(required=True, description='Phone number of the user'),
        'blx': fields.String(required=True, description='thong tin bang lai xe'),
        'bus_id': fields.Integer(required=True, description='bus id ref to bus Table'),
    })
    _driver = api.model('ManagerRegisterDTO', {
        'name': fields.String(required=True, description='First name of the user'),
        'username': fields.String(required=True, description='Username for the user'),
        'email': fields.String(required=True, description='Email address of the user'),
        'phone': fields.String(required=True, description='Phone number of the user'),
        'blx':fields.String(required=True, description='thong tin bang lai xe'),
        'bus_id':fields.Integer(required=True, description='bus id ref to bus Table'),
    })
class Map:
    api = Namespace('map', description='feature for manager')
    roadID = api.model('Road ID', {
        'id':fields.Integer(required=True, description='road id ref to bus Table'),
    })

class Bus:
    api = Namespace('bus', description='feature for bus')
    bus = api.model('get bus data', {
        'bus_id':fields.Integer(required=True, description='road id ref to bus Table'),
        'plate_number': fields.String(required=True, description='Username for the user'),
        'name': fields.String(required=True, description='Email address of the user'),
        'model': fields.String(required=True, description='Phone number of the user'),
        'status': fields.String(required=True, description='thong tin bang lai xe'),
        'route_id':fields.Integer(required=True, description='road id ref to bus Table'),
    })
    start_end = api.model('start_end', {
        'lat': fields.Float(description='Vĩ độ'),
        'lng': fields.Float(description='Kinh độ'),
    })

    latlng = api.model('bus', {
        'start': fields.Nested(start_end, description='Tọa độ điểm bắt đầu'),
        'end': fields.Nested(start_end, description='Tọa độ điểm kết thúc'),
    })

class Feedback:
    api = Namespace('feedback', description='Feature for feedback')
    fb = api.model('Feedback', {
        'feedback_id': fields.Integer(required=True, description='ID của feedback'),
        'feedback_content': fields.String(required=True, description='Nội dung feedback'),
        'feedback_status': fields.String(required=True, description='Trạng thái feedback'),
        'created_at': fields.DateTime(required=True, description='Thời điểm tạo feedback'),
        'bus_number': fields.String(required=True, description='Số xe buýt'),
        'bus_model': fields.String(required=True, description='Model của xe buýt'),
        'user_name': fields.String(required=True, description='Tên người gửi feedback'),
        'driver_name': fields.String(required=True, description='Tên tài xế'),
        'driver_phone': fields.String(required=True, description='Số điện thoại tài xế'),
    })

    pagination = api.model('Pagination', {
        'status': fields.String(required=True, description='Trạng thái kết quả'),
        'message': fields.String(required=True, description='Thông báo'),
        'data': fields.List(fields.Nested(fb), description='Danh sách feedbacks'),
        'total_count': fields.Integer(required=True, description='Tổng số feedbacks'),
        'page': fields.Integer(required=True, description='Trang hiện tại'),
        'page_size': fields.Integer(required=True, description='Số feedbacks mỗi trang'),
    })
    date_range_model = api.model('DateRange', {
        'startDate': fields.String(required=True, description='Start date in yyyy-mm-dd format'),
        'endDate': fields.String(required=True, description='End date in yyyy-mm-dd format')
    })
    _fb = api.model('add_feedback', {
        'bus_id': fields.Integer(required=True, description='Bus ID referencing the Bus Table'),
        'content': fields.String(required=True, description='Content or message of the feedback'),
    })
