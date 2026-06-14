# services/employee_service.py
from werkzeug.security import generate_password_hash
from models.employee import Employee
from models.employee_departments import EmployeeDepartments
from models.employee_roles import EmployeeRole
from models.roles import Role
from db import db
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, DataError

def get_all_employees():
    employees = Employee.query.filter_by(is_deleted=False).options(
        db.joinedload(Employee.department),
        db.joinedload(Employee.roles)
    ).all()
    result = []
    for emp in employees:
        emp_dict = emp.to_dict()
        emp_dict["created_at"] = emp.created_at.isoformat() if emp.created_at else None
        emp_dict["roles"] = [
            {
                "id": role.id,
                "name": role.name,
                "description": role.description
            }
            for role in emp.roles
        ]
        result.append(emp_dict)
    
    return result


def get_all_employees1():
    employees = Employee.query.filter_by(is_deleted=False).all()

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
    # Comprehensive Field Validation
    required_fields = ['name', 'email', 'password', 'department_id']
    for field in required_fields:
        if not data.get(field):
            return False, f"Missing required field: {field}"

    try:
        parent_id_value = data.get('parent_id')
        if parent_id_value == '':
            parent_id_value = None
        hashed_password = generate_password_hash(data['password'])

        new_employee = Employee(
            name=data['name'],
            email=data['email'],
            mob_no=data.get('mob_no'),
            parent_id=parent_id_value,
            department_id=data['department_id'],
            password=hashed_password
        )

        db.session.add(new_employee)
        db.session.commit()

        department_link = EmployeeDepartments(
            employee_id=new_employee.id,
            department_id=data['department_id']
        )
        db.session.add(department_link)

        # Assign default 'Employee' role
        employee_role = Role.query.filter_by(name='Hero').first()
        if employee_role:
            db.session.add(EmployeeRole(employee_id=new_employee.id, role_id=employee_role.id))
        
        db.session.commit()
        return True, new_employee.to_dict()

    except IntegrityError as e:
        db.session.rollback()
        err_msg = str(e.orig).lower() if hasattr(e, 'orig') else str(e).lower()
        if 'email' in err_msg:
            return False, "Email already exists"
        if 'name' in err_msg:
            return False, "Employee name already exists"
        return False, "Data integrity error (possible duplicate or invalid reference)"
    
    except DataError as e:
        db.session.rollback()
        return False, "Invalid data format or value too long"

    except SQLAlchemyError as e:
        db.session.rollback()
        return False, f"Database error: {str(e)}"

    except Exception as e:
        db.session.rollback()
        return False, f"Unexpected error: {str(e)}"
    
def authenticate(email, password):
    employee = Employee.query.filter_by(email=email).first()
    if employee and employee.check_password(password):
        return employee
    return None


def update_employee_by_id(employee_id, data):
    employee = Employee.query.get(employee_id)
    if not employee:
        return {'error': 'Employee not found'}, 404

    try:
        # Update fields
        employee.name = data.get('name', employee.name)
        employee.email = data.get('email', employee.email)
        employee.mob_no = data.get('mob_no', employee.mob_no)
        employee.department_id = data.get('main_department', employee.department_id)

        # Clear old other_departments
        EmployeeDepartments.query.filter_by(employee_id=employee_id).delete()
        other_departments = data.get('other_departments', [])
        for dept_id in other_departments:
            db.session.add(EmployeeDepartments(employee_id=employee_id, department_id=dept_id))

        # Clear old roles
        EmployeeRole.query.filter_by(employee_id=employee_id).delete()
        roles = data.get('roles', [])
        for role_id in roles:
            db.session.add(EmployeeRole(employee_id=employee_id, role_id=role_id))

        db.session.commit()
        return {'message': 'Employee updated successfully'}, 200

    except Exception as e:
        db.session.rollback()
        return {'error': str(e)}, 500

def delete_employee_by_id(employee_id):
    employee = Employee.query.get(employee_id)
    if not employee or employee.is_deleted:
        return {'error': 'Employee not found'}, 404

    try:
        employee.is_deleted = True
        db.session.commit()
        return {'message': 'Employee deleted successfully'}, 200

    except Exception as e:
        db.session.rollback()
        return {'error': str(e)}, 500
