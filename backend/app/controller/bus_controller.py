from flask import request, Blueprint, jsonify, make_response
from flask_pydantic_openapi import Response
from flask_restx import Resource
from pydantic import BaseModel

from app.main import api
from app.main.service.bus_service import get_all_bus, get_st_end, get_bus
from app.main.utils.decorator import token_required
from app.main.utils.dto import Bus
from typing import Dict, Any, List

from app.main.utils.dtov2 import BusDTO

class BusQuery(BaseModel):
    bus_id: int
class Message(BaseModel):
    response: Dict[str, Any]  # response sẽ chứa danh sách các BusDTO
bus_api = Blueprint('bus_api', __name__)

@bus_api.route('/get-all-bus', methods=['GET'])
def list_all_bus():
    return get_all_bus()

@bus_api.route('/get-st-end', methods=['GET'])
def get_bus_location():
    bus_id = request.args.get('bus_id', type=int)
    if not bus_id:
        return {"message": "bus_id is required"}, 400
    return get_st_end(bus_id)
#
# Để validate headers:
@bus_api.route('/get-bus', methods=['GET'])
def get_bus_info():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return {"message": "token is required"}, 400
    return get_bus(data=auth_header)
# @api.route('/get-st-end')
# class ListBus(Resource):
#     @api.doc('lat lng cua xe')
#     @api.marshal_list_with(latlng, envelope='data')
#     def get(self):
#         bus_id = request.args.get('bus_id', type=int)  # Lấy từ query parameters
#         if not bus_id:
#             return {"message": "bus_id is required"}, 400
#         return get_st_end(bus_id)
# @api.route('/get-bus')
# class GetBus(Resource):
#     @api.doc('lay thong tin xe tu token user-taixe')
#     def get(self):
#          # Lấy từ query parameters
#         auth_header = request.headers.get('Authorization')
#         if not auth_header:
#              return {"message": "token is required"}, 400
#         return get_bus(data = auth_header)
