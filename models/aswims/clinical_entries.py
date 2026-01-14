from db import db

class AswimsClinicalEntry(db.Model):
    __tablename__ = 'aswims_clinical_entries'
    
    id = db.Column(db.Integer, primary_key=True)

    patient_id = db.Column(
        db.Integer,
        db.ForeignKey('aswims_patients.id'),
        nullable=False
    )

    daily_notes = db.Column(db.Text, nullable=False)
    medicines = db.Column(db.Text, nullable=True)

    # Logical / clinical date (app-controlled)
    entry_date = db.Column(db.DateTime, nullable=False)

    created_by = db.Column(db.Integer, nullable=False)
    updated_by = db.Column(db.Integer, nullable=True)

    # DB-controlled timestamps (DO NOT override with Python time)
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

    # Relationship
    patient = db.relationship(
        'AswimsPatient',
        backref=db.backref('clinical_entries', lazy=True)
    )

    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "daily_notes": self.daily_notes,
            "medicines": self.medicines,
            "entry_date": self.entry_date.isoformat() if self.entry_date else None,
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
