# models/employee.py
from db import db

class Employee(db.Model):
    __tablename__ = 'employees'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True, nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    mob_no = db.Column(db.String(20), nullable=True)
    department_id = db.Column(db.Integer, nullable=True)
    parent_id = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'mob_no': self.mob_no,
            'parent_id': self.parent_id,
            'department_id': self.department_id
            # ❗️ Don't include the password
        }