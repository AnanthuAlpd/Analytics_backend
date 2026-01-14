from db import db

class AswimsSpecialities(db.Model):
    __tablename__ = 'aswims_specialities'
    
    id = db.Column(db.Integer, primary_key=True)
    speciality_name = db.Column(db.String(100), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('aswims_specialities.id'), nullable=True)
    
    # Self-referencing relationship for Super Specialities
    sub_specialities = db.relationship('AswimsSpecialities', 
                                       backref=db.backref('parent', remote_side=[id]), 
                                       lazy=True)

    