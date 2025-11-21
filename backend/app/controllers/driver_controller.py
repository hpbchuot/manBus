from flask import request, Blueprint
from app.main import api
from app.main.service.noti_service import get_list_noti, mark_read

noti_api = Blueprint('noti_api', __name__)

@noti_api.route('/get-list',methods=['GET'])
def NotiList():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return {"message": "token is required"}, 400
    #print(auth_header)
    return get_list_noti(data=auth_header)
@noti_api.route('/<int:noti>/read', methods=['PUT'])
def mark_notification_as_read(noti):
    print(noti)
    return mark_read(noti)
