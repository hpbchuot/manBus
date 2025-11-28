# Security configurations (JWT secret, etc.)
import os
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your_default_jwt_secret_key')