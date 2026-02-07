from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Assuming 'db' is imported from your main app or a shared extension file
from db import db 

class AswimsWard(db.Model):
    __tablename__ = 'aswims_wards'
    
    id = db.Column(db.Integer, primary_key=True)
    ward_name = db.Column(db.String(100), unique=True, nullable=False)
    ward_code = db.Column(db.String(10), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "ward_name": self.ward_name,
            "ward_code": self.ward_code
        }