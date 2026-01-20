from datetime import datetime
from db import db

class PatientMedicine(db.Model):
    """Transactional table for patient-specific medication prescriptions."""
    __tablename__ = 'aswims_patient_medicines'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('aswims_patients.id'), nullable=False)
    
    # Links to master tables
    category_id = db.Column(db.Integer, db.ForeignKey('aswims_medicine_categories.id'), nullable=True)
    frequency_id = db.Column(db.Integer, db.ForeignKey('aswims_medicine_frequencies.id'), nullable=True)
    
    medicine_name = db.Column(db.String(255), nullable=False)
    dose = db.Column(db.String(50), nullable=True)  # e.g., '500mg' or '1.2g'
    
    # Store daily_count here for specific circle grid rendering
    daily_count = db.Column(db.Integer, default=1)
    
    remarks = db.Column(db.Text, nullable=True)     # e.g., 'After food'
    is_active = db.Column(db.Boolean, default=True) # Used to discontinue a medicine
    
    # Metadata
    created_by = db.Column(db.Integer, db.ForeignKey('aswims_users.id'), nullable=False)
    # Updated Timestamp Logic
    created_at = db.Column(
        db.TIMESTAMP,
        server_default=db.func.current_timestamp(),
        nullable=True
    )

    updated_at = db.Column(
        db.TIMESTAMP,
        server_default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp(),
        nullable=True
    )

    # Relationships to fetch names easily in the frontend
    category = db.relationship('MedicineCategory', backref='patient_meds')
    frequency = db.relationship('MedicineFrequency', backref='patient_meds')

    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "medicine_name": self.medicine_name,
            "category": self.category.category_name if self.category else None,
            "dose": self.dose,
            "frequency": self.frequency.frequency_name if self.frequency else None,
            "daily_count": self.daily_count,
            "remarks": self.remarks,
            "is_active": self.is_active,
            "created_at": self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }