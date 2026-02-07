from db import db

class AswimsPatientVitals(db.Model):
    __tablename__ = 'aswims_patient_vitals'
    
    id = db.Column(db.Integer, primary_key=True)

    patient_id = db.Column(
        db.Integer,
        db.ForeignKey('aswims_patients.id'),
        nullable=False
    )

    temp = db.Column(db.Numeric(4, 1))    # e.g., 37.5
    pulse = db.Column(db.Integer)         # e.g., 85
    bp = db.Column(db.String(10))         # e.g., "120/80"
    spo2 = db.Column(db.Integer)          # e.g., 98
    resp_rate = db.Column(db.Integer)     # e.g., 18

    # Logical / clinical timestamp (app-controlled)
    recorded_at = db.Column(db.DateTime, nullable=False)

    created_by = db.Column(db.Integer, nullable=False)

    # DB-controlled audit timestamp
    created_at = db.Column(
        db.TIMESTAMP,
        server_default=db.func.current_timestamp(),
        nullable=True
    )

    # Relationship
    patient = db.relationship(
        'AswimsPatient',
        backref=db.backref('vitals', lazy=True)
    )

    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "temp": float(self.temp) if self.temp else None,
            "pulse": self.pulse,
            "bp": self.bp,
            "spo2": self.spo2,
            "resp_rate": self.resp_rate,
            "recorded_at": self.recorded_at.isoformat() if self.recorded_at else None,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
