from app.extensions import db
from datetime import datetime

class Collection(db.Model):
    __tablename__ = 'collections'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.String(50))
    client_name = db.Column(db.String(255))
    phone = db.Column(db.String(50))
    email = db.Column(db.String(255))
    due_date = db.Column(db.Date)
    amount = db.Column(db.Numeric(10, 2))
    days_overdue = db.Column(db.Integer)
    status = db.Column(db.String(50))
    last_management = db.Column(db.Date)
    observations = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)