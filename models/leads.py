from datetime import datetime
from db import db
from models.employee import Employee 
from models.lead_status import LeadStatus
from models.lead_source import LeadSource

class Lead(db.Model):
    __tablename__ = 'leads'

    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    lead_cat = db.Column(db.Enum('Client', 'Employee'), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    mob_no = db.Column(db.String(15), nullable=True)
    remarks = db.Column(db.Text, nullable=True)
    follow_up_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    status_id = db.Column(db.Integer, db.ForeignKey('lead_status.id'), nullable=True)
    lead_source_id = db.Column(db.Integer, db.ForeignKey('lead_sources.id'), nullable=True)

    # Optional relationship if you want backref to Employee model
    employee = db.relationship('Employee', backref='leads')
    status_rel = db.relationship('LeadStatus', backref='leads')
    source_rel = db.relationship('LeadSource', backref='leads')
