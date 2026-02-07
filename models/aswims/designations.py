from db import db

class AswimsDesignations(db.Model):
    __tablename__ = 'aswims_designations'
    
    id = db.Column(db.Integer, primary_key=True)
    designation_name = db.Column(db.String(100), nullable=False)
    hierarchy_level = db.Column(db.Integer, nullable=False)
    
    # FIX: Use string 'AswimsUsers' instead of the class object
    # This allows SQLAlchemy to resolve the name later
    users = db.relationship('AswimsUsers', backref='appointment', lazy=True)