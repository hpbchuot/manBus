from .. import db
from app.main.model.map import BusRoute
from geoalchemy2 import Geometry
from typing import Optional
from pydantic import BaseModel

class Bus(db.Model):
    """ Bus Model for storing bus-related details """
    __tablename__ = "bus"

    bus_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    plate_number = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=True)
    model = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(20), default='Active')
    route_id = db.Column(db.Integer, db.ForeignKey('routes.route_id'), nullable=True)
    current_location = db.Column(Geometry('POINT', srid=4326), nullable=True)  # PostGIS Point geometry

    # Foreign Key to Routes table, assuming Route table exists with a primary key of route_id
    route_id = db.Column(db.Integer, db.ForeignKey('road.id'), nullable=False)

    # Relationship with Route
    road = db.relationship('BusRoute', backref='buses', lazy=True)


    def __init__(self, plate_number, name, model, status, route_id, current_location):
        self.plate_number = plate_number
        self.name = name
        self.model = model
        self.status = status
        self.route_id = route_id
        self.current_location = current_location
    def __repr__(self):
        return f"<Bus {self.name} - {self.plate_number}>"

class BusBase(BaseModel):
    plate_number: str
    name: Optional[str] = None
    model: Optional[str] = None
    status: Optional[str] = 'Active'
    route_id: Optional[int] = None
    current_location: Optional[str] = None  # WKT format (e.g., 'POINT(lon lat)')

class BusCreate(BusBase):
    pass

# Model for Bus update (PUT)
class BusUpdate(BusBase):
    pass

# Model for Bus response (GET)
class BusOut(BaseModel):
    bus_id: int
    plate_number: str
    name: Optional[str] = None
    model: Optional[str] = None
    status: str
    route_id: Optional[int] = None
    current_location: Optional[str] = None  # WKT

    class Config:
        from_attributes = True
