from flask import request, Blueprint
from flask_pydantic_openapi import Request
from flask_restx import Resource
from app.main import api
from app.main.service.manager_service import create, get_all_manager, create_driver, get_all_driver, delete_user, \
    delete_tai_xe,update_driver,get_all_user
from ..utils.dto import UserDto, ManDto
from ..utils.dtov2 import ManagerRegisterDTO, DriverRegisterDTO

# api = ManDto.api
# _manager = ManDto.manager
# user = ManDto.manager
# man = ManDto.man_register
# driver = ManDto.driver_register
# driverUpdate = ManDto.driver_update
manager_api = Blueprint('manager_api', __name__)

@manager_api.route('/get-all-driver')
def DriverList():
    page = request.args.get('page', 1, type=int)
    pageSize = request.args.get('pageSize', 10, type=int)
    return get_all_driver(page, pageSize)
# @api.route('/')
# class ManagerList(Resource):
#     @api.doc('list_of_registered_users')
#     @api.marshal_list_with(_manager, envelope='data')
#     def get(self):
#         """List all registered users"""
#         return get_all_manager()
@manager_api.route('/', methods=['GET'])
def listManager():
    return get_all_manager()
@manager_api.route('/get-all-user', methods=['GET'])
def UserList():
    page = request.args.get('page', 1, type=int)
    pageSize = request.args.get('pageSize', 10, type=int)
    return get_all_user(page, pageSize)

@manager_api.route('/create-manager',methods=['POST'])
@api.validate(
    body=Request(ManagerRegisterDTO),
    tags=['manager']
)
def CreateManager():
    data = request.context.body
    print("check",data)
    return create(data)

@manager_api.route('/create-driver',methods=['POST'])
@api.validate(
    body=Request(DriverRegisterDTO),
    tags=['manager']
)
def CreateDriver():
    data = request.context.body
    return create_driver(data)
# @api.route('/update-manager')
# class UpdateDriver(Resource):
#     """
#         User Login Resource
#     """
#     @api.doc('Update manager')
#     @api.expect(driverUpdate, validate=True)
#     def post(self):
#         # get the post data
#         post_data = request.json
#         return update_manager(data=post_data)
# @api.route('/update-driver')
# class UpdateDriver(Resource):
#     """
#         User Login Resource
#     """
#     @api.doc('Update driver')
#     @api.expect(driverUpdate, validate=True)
#     def post(self):
#         # get the post data
#         post_data = request.json
#         return update_driver(data=post_data)
# @api.route('/delete-user')
# class DeleteUser(Resource):
#     @api.doc('delete user')
#     @api.expect(user, validate=True)
#     def post(self):
#         # get the post data
#         post_data = request.json
#         return delete_user(data=post_data)
# @api.route('/delete-driver')
# class DeleteUser(Resource):
#     @api.doc('Xóa tài xế')
#     @api.expect(user, validate=True)
#     def post(self):
#         # get the post data
#         post_data = request.json
#         return delete_tai_xe(data=post_data)
