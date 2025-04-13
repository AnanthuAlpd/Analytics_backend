from werkzeug.security import generate_password_hash, check_password_hash
from models.user_model import find_user_by_email, insert_user

def register_user(username, email, password, confirm_password):
    if not all([username, email, password, confirm_password]):
        return {'error': 'All fields are required'}, 400
    if password != confirm_password:
        return {'error': 'Passwords do not match'}, 400
    if find_user_by_email(email):
        return {'error': 'User already exists'}, 400
    hashed = generate_password_hash(password)
    insert_user(username, email, hashed)
    return {'message': 'Registered successfully'}, 201

def login_user(email, password):
    user = find_user_by_email(email)
    if not user or not check_password_hash(user['password'], password):
        return {'error': 'Invalid credentials'}, 401
    return {'message': 'Login successful', 'user': {
        'id': user['id'], 'username': user['username'], 'email': user['email']
    }}, 200

def get_all_users():
    from db import mysql
    try:
        with mysql.connection.cursor() as cursor:
            cursor.execute("SELECT id, username, email FROM users")
            users = cursor.fetchall()
            return {'users': users}, 200
    except Exception as e:
        return {'error': str(e)}, 500
