# # app/__init__.py
#
# from flask_restx import Api
# from flask import Blueprint
#
# from .main.controller.user_controller import api as user_ns
# from .main.controller.auth_controller import api as auth_ns
# from .main.controller.manager_controller import api as man
# from .main.controller.map_controller import api as map
# from .main.controller.bus_controller import api as bus
# from .main.controller.feedback_controller import api as feedback
# blueprint = Blueprint('api', __name__)
#
# api = Api(blueprint,
#           title='FLASK RESTPLUS API FOR BUSMANAGE',
#           version='1.0',
#           description='a boilerplate for flask restplus web service'
#           )
#
# api.add_namespace(user_ns, path='/user')
# api.add_namespace(auth_ns)
# api.add_namespace(man)
# api.add_namespace(map)
# api.add_namespace(bus)
# api.add_namespace(feedback)
# app/main/api.py

from flask import Blueprint
from flask_pydantic_openapi import FlaskPydanticOpenapi

from app.main.controller.noti_controller import noti_api
from app.main.controller.user_controller import user_api
from app.main.controller.auth_controller import auth_api
from app.main.controller.manager_controller import manager_api
from app.main.controller.map_controller import map_api
from app.main.controller.bus_controller import bus_api
from app.main.controller.feedback_controller import feedback_api
from app.main.controller.noti_controller import noti_api
# Khởi tạo Blueprint cho API
blueprint = Blueprint('api', __name__)

# Đăng ký các controller vào blueprint
blueprint.register_blueprint(user_api, url_prefix='/user')
blueprint.register_blueprint(auth_api, url_prefix='/auth')
blueprint.register_blueprint(manager_api, url_prefix='/manager')
blueprint.register_blueprint(map_api, url_prefix='/map')
blueprint.register_blueprint(bus_api, url_prefix='/bus')
blueprint.register_blueprint(feedback_api, url_prefix='/feedback')
blueprint.register_blueprint(noti_api, url_prefix='/notifications')

