from datetime import datetime
from db import db

class LeadActivityLog(db.Model):
    __tablename__ = 'lead_activity_logs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    lead_id = db.Column(db.Integer, db.ForeignKey('leads.id', ondelete='CASCADE'), nullable=False)
    emp_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    action_type = db.Column(
        db.Enum('Lead Created', 'Status Change', 'Note Added', 'Contact Attempt'),
        nullable=False
    )
    details = db.Column(db.Text, nullable=True)
    old_value = db.Column(db.String(100), nullable=True)
    new_value = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Relationships
    lead = db.relationship('Lead', backref=db.backref('activities', cascade='all, delete-orphan'))
    employee = db.relationship('Employee', backref='lead_activities')
