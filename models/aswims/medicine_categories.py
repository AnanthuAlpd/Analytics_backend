from db import db

class MedicineCategory(db.Model):
    """Master table for medicine categories like Antibiotics, Analgesics, etc."""
    __tablename__ = 'aswims_medicine_categories'

    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(255), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "category_name": self.category_name,
            "description": self.description
        }