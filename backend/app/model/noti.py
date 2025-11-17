from datetime import datetime
from .. import db  # Assuming you're using Flask-SQLAlchemy

class Notification(db.Model):
    """ Notification Model for storing notification details """
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Primary Key
    message = db.Column(db.String(255), nullable=False)  # Notification message
    read = db.Column(db.Boolean, nullable=False, default=False)  # Notification read status
    created_at = db.Column(db.TIMESTAMP, nullable=False, default=datetime.utcnow)  # Created timestamp
    type = db.Column(db.String(50), nullable=True)  # Optional: Type of notification
    link = db.Column(db.String(255), nullable=True)  # Optional: Link for the notification
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Foreign Key to User

    # Relationship with User model
    user = db.relationship('User', backref='notifications', lazy=True)

    def __repr__(self):
        return f"<Notification {self.id} - {self.message[:50]}>"

