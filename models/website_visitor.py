from db import db
from datetime import datetime

class WebsiteVisitor(db.Model):
    __tablename__ = 'website_visitors'

    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45), nullable=False)  # Supports both IPv4 and IPv6
    visit_time = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "ip_address": self.ip_address,
            "visit_time": self.visit_time.isoformat()
        }
