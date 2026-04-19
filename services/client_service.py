# services/client_service.py

from models.clients import Client, db, generate_password_hash
from models.roles import Role
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, DataError

def get_all_clients():
    return Client.query.filter_by(is_deleted=False).all()

def add_client(data):
    # Validation
    required_fields = ['name', 'email', 'password']
    for field in required_fields:
        if not data.get(field):
            return False, f"Missing required field: {field}"

    try:
        hashed_password = generate_password_hash(data['password'])
        new_client = Client(
            name=data['name'],
            email=data['email'],
            phone=data.get('mob_no'),
            ref_emp_id=data.get('parent_id'),
            service_id=data.get('service_id'),
            password=hashed_password
        )

        # Assign default 'client' role
        client_role = Role.query.filter_by(name='client').first()
        if client_role:
            new_client.role_id = client_role.id

        db.session.add(new_client)
        db.session.commit()
        return True, new_client

    except IntegrityError as e:
        db.session.rollback()
        err_msg = str(e.orig).lower() if hasattr(e, 'orig') else str(e).lower()
        if 'email' in err_msg:
            return False, "Email already exists"
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

def delete_client_by_id(client_id):
    client = Client.query.get(client_id)
    if not client or client.is_deleted:
        return {'error': 'Client not found'}, 404

    try:
        client.is_deleted = True
        db.session.commit()
        return {'message': 'Client deleted successfully'}, 200

    except Exception as e:
        db.session.rollback()
        return {'error': str(e)}, 500
