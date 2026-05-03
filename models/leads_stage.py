from db import db

class LeadsStage(db.Model):
    __tablename__ = 'leads_stage'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    stage_name = db.Column(db.String(100), nullable=False)
    day_number = db.Column(db.Integer, nullable=False)
    order_no = db.Column(db.Integer, nullable=False)
    next_stage_id = db.Column(db.Integer, nullable=True)
    delay_days = db.Column(db.Integer, default=1)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    actions = db.relationship('LeadsStageAction', backref='lead_stage_rel', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            "id": self.id,
            "stage_name": self.stage_name,
            "day_number": self.day_number,
            "order_no": self.order_no,
            "next_stage_id": self.next_stage_id,
            "delay_days": self.delay_days,
            "is_active": self.is_active,
            "actions": [action.to_dict() for action in self.actions] if self.actions else []
        }
