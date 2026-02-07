from db import db

class EmployeeRole(db.Model):
    __tablename__ = 'employee_roles'

    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id', ondelete='CASCADE'), primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True)

    # employee = db.relationship('Employee', back_populates='employee_roles')
    # role = db.relationship('Role', back_populates='employee_roles')