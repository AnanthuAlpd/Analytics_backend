from db import db
from werkzeug.security import generate_password_hash, check_password_hash

class Employee(db.Model):
    __tablename__ = 'employees'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True, nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    mob_no = db.Column(db.String(20), nullable=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    parent_id = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())

    # Relationships
    department = db.relationship("Department", back_populates="employees")

    
    roles = db.relationship(
        'Role',
        secondary='employee_roles',
        lazy='select',
        backref=db.backref('employees', lazy='select')
    )

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)

    def to_dict(self):
        other_departments = [
            {
                'id': ed.department.id,
                'name': ed.department.name
            }
            for ed in getattr(self, 'employee_departments', [])
            if ed.department_id != self.department_id
        ]

        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'mob_no': self.mob_no,
            'parent_id': self.parent_id,
            'department_id': self.department_id,
            'main_department': self.department.name if self.department else None,
            'other_departments': other_departments,
            'roles': [{'id': role.id, 'name': role.name} for role in self.roles]
        }

# Import at the end to avoid circular imports
from models.employee_roles import EmployeeRole
from models.roles import Role
