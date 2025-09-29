from models.roles import Role
from db import db

def get_all_roles():

    roles=Role.query.all()

    result=[
        {
            'id':d.id,
            'name':d.name,
            'description':d.description
        }
        for d in roles
    ]
    return result
def create_role(data):
    new_role = Role(
        name=data.get('name'),
        description=data.get('description')
    )
    db.session.add(new_role)
    db.session.commit()
    return {
        'id': new_role.id,
        'name': new_role.name,
        'description': new_role.description
    }


def update_role(role_id, data):
    role = Role.query.get(role_id)
    if not role:
        return None

    role.name = data.get('name', role.name)
    role.description = data.get('description', role.description)

    db.session.commit()
    return {
        'id': role.id,
        'name': role.name,
        'description': role.description
    }


def delete_role(role_id):
    role = Role.query.get(role_id)
    if not role:
        return False

    db.session.delete(role)
    db.session.commit()
    return True