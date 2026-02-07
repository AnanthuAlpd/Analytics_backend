from models.department import Department
from db import db

def get_all_departments():

    departments=Department.query.all()

    result=[
        {
            'id':d.id,
            'name':d.name
        }
        for d in departments
    ]
    return result
def create_department(data):
    """Create a new department"""
    new_department = Department(name=data['name'])
    db.session.add(new_department)
    db.session.commit()
    return {'id': new_department.id, 'name': new_department.name}


def update_department(department_id, data):
    """Update an existing department"""
    department = Department.query.get(department_id)
    if not department:
        return None

    department.name = data.get('name', department.name)
    db.session.commit()
    return {'id': department.id, 'name': department.name}