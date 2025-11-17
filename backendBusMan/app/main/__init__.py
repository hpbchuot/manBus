from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS  # Import Flask-CORS
from flask_pydantic_openapi import FlaskPydanticOpenapi
from .config import config_by_name

db = SQLAlchemy()
flask_bcrypt = Bcrypt()

api = FlaskPydanticOpenapi('flask')
def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    api.register(app)
    db.init_app(app)
    flask_bcrypt.init_app(app)

    # Thêm CORS vào ứng dụng
    CORS(
        app,
        resources={r"/*": {
            "origins": ["http://localhost:3000"],
            "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization","Accept"],
            # only set this to True if you actually use cookies/withCredentials

        }},
    supports_credentials=False


    )


    return app
