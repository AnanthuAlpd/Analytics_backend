from db import db
class MedicineFrequency(db.Model):
    """Master table for dose frequencies."""
    __tablename__ = 'aswims_medicine_frequencies'

    id = db.Column(db.Integer, primary_key=True)
    frequency_name = db.Column(db.String(20), nullable=False, unique=True)
    description = db.Column(db.String(100), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "frequency_name": self.frequency_name,
            "description": self.description
        }