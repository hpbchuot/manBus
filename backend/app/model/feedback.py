from datetime import datetime
from .. import db
from app.main.model.bus import Bus  # Import model Bus
from app.main.model.user import User  # Import model User

class Feedback(db.Model):
    """ Feedback Model for storing user feedback related to buses """
    __tablename__ = "feedback"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Primary Key
    status = db.Column(db.String(20), nullable=False)  # Feedback status (e.g., pending, resolved)
    content = db.Column(db.Text, nullable=False)  # Feedback content or message
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Timestamp when feedback is created
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Timestamp when feedback is updated

    # Foreign key to Bus table
    bus_id = db.Column(db.Integer, db.ForeignKey('bus.bus_id'), nullable=False)
    bus = db.relationship('Bus', backref='feedbacks', lazy=True)  # Relationship to Bus

    # Foreign key to User table
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='feedbacks', lazy=True)  # Relationship to User

    def __repr__(self):
        return f"<Feedback {self.id} - Bus ID: {self.bus_id}, User ID: {self.user_id}>"
