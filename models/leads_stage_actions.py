from db import db

class LeadsStageAction(db.Model):
    __tablename__ = 'leads_stage_actions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    stage_id = db.Column(db.Integer, db.ForeignKey('leads_stage.id', ondelete='CASCADE'), nullable=False)
    action_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_mandatory = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            "id": self.id,
            "stage_id": self.stage_id,
            "action_name": self.action_name,
            "description": self.description,
            "is_mandatory": self.is_mandatory
        }
