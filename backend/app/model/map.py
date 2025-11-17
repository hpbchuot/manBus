from .. import db
from datetime import datetime
from geoalchemy2 import Geometry
from geoalchemy2.types import Geometry
class BusRoute(db.Model):
    __tablename__ = 'road'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    route_geom = db.Column(Geometry('LINESTRING', srid=4326))  # Geometry for the route
    stops = db.Column(Geometry('MULTIPOINT', srid=4326))  # Multiple points for stops
    current_segment = db.Column(db.Integer)
    updated_at = db.Column(db.DateTime, default=datetime.now)