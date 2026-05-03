from db import db

class LeadsSource(db.Model):
    __tablename__ = 'leads_sources'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    source_name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def to_dict(self):
        return {
            "id": self.id,
            "source_name": self.source_name,
            "description": self.description,
            "is_active": self.is_active
        }
