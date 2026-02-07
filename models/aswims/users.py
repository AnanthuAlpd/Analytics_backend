from db import db
from datetime import datetime

class AswimsUsers(db.Model):
    __tablename__ = 'aswims_users'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email_id = db.Column(db.String(100), unique=True, nullable=True)
    mob_no = db.Column(db.String(15), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Foreign Keys linking to other files
    designation_id = db.Column(db.Integer, db.ForeignKey('aswims_designations.id'), nullable=False)
    speciality_id = db.Column(db.Integer, db.ForeignKey('aswims_specialities.id'), nullable=True)
    super_speciality_id = db.Column(db.Integer, db.ForeignKey('aswims_specialities.id'), nullable=True)
    
    account_status = db.Column(db.Enum('Active', 'Inactive', 'Pending'), default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Explicitly define relationships to match your Service calls
    speciality = db.relationship('AswimsSpecialities', foreign_keys=[speciality_id])
    super_speciality = db.relationship('AswimsSpecialities', foreign_keys=[super_speciality_id])