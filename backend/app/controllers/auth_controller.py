from flask import request, Blueprint, current_app
from ..services.auth.auth_service import AuthService

auth_api = Blueprint('auth_api', __name__)

@auth_api.route('/register', methods=['POST'])
def register_user():
    # Access request JSON data
    data = request.get_json()
    print('User registration logic...')
    # Get db instance from app context
    db = current_app.config['db']

    # Convert dict to object for attribute access
    from types import SimpleNamespace
    data_obj = SimpleNamespace(**data)

    return AuthService.register(db, data_obj).toJson()

# @auth_api.route('/refresh-token', methods=['POST'])
# @api.validate(
#     body=Request(RefreshTokenDTO),  # Validate the request body using the Pydantic model
#     resp=Response(HTTP_200=Message, HTTP_400=Message),  # Example response
#     tags=['auth']
# )
# def refresh_token():
#     data = request.context.body
#     return Auth.get_refresh_token(data=data)
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