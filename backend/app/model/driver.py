from .. import db, flask_bcrypt
from app.main.model.bus import Bus  # Import the Bus model
from app.main.model.user import User  # Import the Bus model
import datetime
import jwt
from app.main.model.blacklist import BlacklistToken
from ..config import key


class Driver(db.Model):
    """ Driver Model for storing driver-related details """
    __tablename__ = "driver"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    license_number = db.Column(db.String(100), nullable=False, unique=True)

    # Define the bus_id as a foreign key that references the Bus table's id
    bus_id = db.Column(db.Integer, db.ForeignKey('bus.bus_id'), nullable=False)

    # You can also define the relationship between Driver and Bus for easy access
    bus = db.relationship('Bus', backref='drivers', lazy=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # You can also define the relationship between Driver and Bus for easy access
    user = db.relationship('User', backref='drivers', lazy=True)
    status = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return "<Driver '{}'>".format(self.license_number)
