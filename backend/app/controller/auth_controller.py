from flask import request, Blueprint
from flask_pydantic_openapi import Request, Response
from flask_restx import Resource
from pydantic import BaseModel

from app.main import api
from app.main.service.auth_helper import Auth
from app.main.utils.dtov2 import AuthDTO, RefreshTokenDTO
from typing import Dict, Any
class Message(BaseModel):
    response: Dict[str, Any]

auth_api = Blueprint('auth_api', __name__)
@auth_api.route('/login', methods=['POST'])
@api.validate(
    body=Request(AuthDTO),
    resp=Response(HTTP_200=Message, HTTP_400=Message),
    tags=['user']
)
def register_user():
    # Access validated request data
    data = request.context.body  # This is the validated data
    print('User registration logic...')
    return Auth.login_user(data)

@auth_api.route('/refresh-token', methods=['POST'])
@api.validate(
    body=Request(RefreshTokenDTO),  # Validate the request body using the Pydantic model
    resp=Response(HTTP_200=Message, HTTP_400=Message),  # Example response
    tags=['auth']
)
def refresh_token():
    data = request.context.body
    return Auth.get_refresh_token(data=data)
#
#
# @api.route('/logout')
# class LogoutAPI(Resource):
#     """
#     Logout Resource
#     """
#     @api.doc('logout a user')
#     def post(self):
#         # get auth token
#         auth_header = request.headers.get('Authorization')
#         return Auth.logout_user(data=auth_header)