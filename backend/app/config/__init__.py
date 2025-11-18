from dotenv import load_dotenv
import os

load_dotenv()

key = os.getenv('SECRET_KEY', 'my_precious_secret_key')