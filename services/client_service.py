# services/client_service.py

from models.clients import Client, db,generate_password_hash

def get_all_clients():
    return Client.query.all()

def add_client(data):
    hashed_password = generate_password_hash(data['password'])
    new_client = Client(
        name=data['name'],
        email=data['email'],
        phone=data.get('mob_no'),
        ref_emp_id=data.get('parent_id'),
        service_id=data.get('service_id'),
        password=hashed_password
    )
    db.session.add(new_client)
    db.session.commit()
    return new_client
