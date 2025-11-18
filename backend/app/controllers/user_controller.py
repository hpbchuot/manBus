from flask import request, Blueprint, jsonify
from flask_pydantic_openapi import Request, Response
from pydantic import BaseModel, EmailStr, ValidationError
from app.main.utils.dtov2 import UserRegisterDTO
from app.main import api
from ..services.user.user_service import save_new_user, get_all_users, get_a_user
from typing import Dict, Any
class Message(BaseModel):
    response: Dict[str, Any]

# Create the Blueprint
user_api = Blueprint('api', __name__)

# Register the endpoint
@user_api.route('/register', methods=['POST'])
@api.validate(
    body=Request(UserRegisterDTO),
    tags=['user']
)
def register_user():
    # Access validated request data
    data = request.context.body  # This is the validated data
    print('User registration logic...',data)
    return save_new_user(data)

#
#
# @api.route('/<public_id>')
# @api.param('public_id', 'The User identifier')
# @api.response(404, 'User not found.')
# class User(Resource):
#     @api.doc('get a user')
#     @api.marshal_with(_user)
#     def get(self, public_id):
#         """get a user given its identifier"""
#         user = get_a_user(public_id)
#         if not user:
#             api.abort(404)
#         else:
#             return user
