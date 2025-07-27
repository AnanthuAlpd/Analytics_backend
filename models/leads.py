from datetime import datetime
from db import db
from models.employee import Employee 

class Lead(db.Model):
    __tablename__ = 'leads'

    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    lead_cat = db.Column(db.Enum('Client', 'Employee'), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    mob_no = db.Column(db.String(15), nullable=True)
    lead_source = db.Column(db.String(50), nullable=True)
    status = db.Column(
        db.Enum('New', 'Contacted', 'Converted', 'Rejected'),
        default='New'
    )
    remarks = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    # Optional relationship if you want backref to Employee model
    employee = db.relationship('Employee', backref='leads')
