import uuid
import datetime

from sqlalchemy import or_

from app.main import db
from app.main.model.user import User

def to_pascal_case(name):
    # Tách chuỗi thành các từ, viết hoa chữ cái đầu của mỗi từ, sau đó nối lại với nhau
    return ' '.join(word.capitalize() for word in name.split())

def save_new_user(data):
    user = User.query.filter(
        or_(
            User.email == data.email,
            User.phone == data.phone,
            User.username == data.username
        )
    ).first()
    if not user:
        pascal_case_name = to_pascal_case(data.fname) + " " + to_pascal_case(data.lname)
        new_user = User(
            public_id=str(uuid.uuid4()),
            email=data.email,
            name = pascal_case_name,
            phone=data.phone,
            admin=False,
            username=data.username,
            password=data.password,
            registered_on=datetime.datetime.utcnow()
        )
        save_changes(new_user)
        return generate_token(new_user)
    else:
        response_object = {
            'status': 'fail',
            'message': 'User already exists. Please Log in.',
        }
        return response_object, 400


def get_all_users():
    return User.query.all()


def get_a_user(public_id):
    return User.query.filter_by(public_id=public_id).first()


def save_changes(data):
    db.session.add(data)
    db.session.commit()

def generate_token(user):
    try:
        # generate the auth token
        auth_token = user.encode_auth_token(user,1)
        response_object = {
            'status': 'success',
            'message': 'Successfully registered.',
            'Authorization': auth_token
        }
        return response_object, 201
    except Exception as e:
        response_object = {
            'status': 'fail',
            'message': 'Some error occurred. Please try again.'
        }
        return response_object, 401