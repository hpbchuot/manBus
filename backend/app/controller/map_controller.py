from flask import request, Blueprint
from flask_restx import Resource
from app.main import api
from app.main.service.map_service import get_location
from app.main.utils.dto import Map

# api = Map.api
# roadID = Map.roadID
map_api = Blueprint('map_api', __name__)

@map_api.route('/get-location',methods=['POST'])
def DriverList():
    print(request.json)
    post_data = request.json
    return get_location(post_data)
