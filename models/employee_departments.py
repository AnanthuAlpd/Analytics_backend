from db import db  # adjust the import to your app structure

class EmployeeDepartments(db.Model):
    __tablename__ = 'employee_departments'

    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), primary_key=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), primary_key=True)

    # Optional relationships (if you need to back-reference)
    employee = db.relationship('Employee', backref=db.backref('employee_departments', lazy='dynamic'))
    department = db.relationship('Department', backref=db.backref('employee_departments', lazy='dynamic'))
