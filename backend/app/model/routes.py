# from .. import db
#
# class Route(db.Model):
#     """ Route Model for storing route-related details """
#     __tablename__ = "route"
#
#     route_id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Primary Key
#     route_name = db.Column(db.String(100), nullable=False)  # Name of the route
#     stops = db.Column(db.ARRAY(db.Integer), nullable=False)  # Array of stop IDs (assuming stop IDs are integers)
#     duration = db.Column(db.Integer, nullable=False)  # Average duration in minutes
#
#     def __repr__(self):
#         return f"<Route {self.route_name}>"
