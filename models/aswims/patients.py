from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from db import db

class AswimsPatient(db.Model):
    __tablename__ = 'aswims_patients'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    ward_id = db.Column(db.Integer, db.ForeignKey('aswims_wards.id'), nullable=False)
    bed_no = db.Column(db.String(20), nullable=False)
    diagnosis = db.Column(db.Text, nullable=False)
    doa = db.Column(db.DateTime, nullable=False)
    
    status = db.Column(db.Enum('Admitted', 'Discharged', 'Transferred'), default='Admitted')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer) # Staff ID from JWT

    # Relationship to fetch ward info directly from patient object
    ward = db.relationship('AswimsWard', backref='patients')

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "ward_name": self.ward.ward_name if self.ward else "Unknown",
            "bed_no": self.bed_no,
            "diagnosis": self.diagnosis,
            "doa": self.doa.strftime('%Y-%m-%d %H:%M:%S'),
            "status": self.status
        }