# services/employee_service.py
from werkzeug.security import generate_password_hash
from models.employee import Employee
from db import db
from sqlalchemy.exc import SQLAlchemyError

def get_all_employees():
    employees = Employee.query.all()

    result = [
        {
            "id": emp.id,
            "name": emp.name,
            "email": emp.email,
            "mob_no": emp.mob_no,
            "department_id": emp.department_id,
            "parent_id": emp.parent_id,
            "created_at": emp.created_at.isoformat() if emp.created_at else None
        }
        for emp in employees
    ]

    return result

def add_employee(data):
    try:
        parent_id_value = data.get('parent_id')
        if parent_id_value == '':
            parent_id_value = None
        hashed_password = generate_password_hash(data['password'])

        new_employee = Employee(
            name=data['name'],
            email=data['email'],
            mob_no=data['mob_no'],
            parent_id=parent_id_value,
            department_id=data['department_id'],
            password=hashed_password
        )

        db.session.add(new_employee)
        db.session.commit()

        return True, new_employee.to_dict()
    except SQLAlchemyError as e:
        db.session.rollback()
        return False, str(e)
    
def authenticate(email, password):
    employee = Employee.query.filter_by(email=email).first()
    if employee and employee.check_password(password):
        return employee
    return None