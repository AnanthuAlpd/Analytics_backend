from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import cross_origin
from db import mysql


auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
@cross_origin(origin='http://localhost:4200')
def register():
    data = request.json

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    confirm_password = data.get('confirm_password')

    if not all([username, email, password, confirm_password]):
        return jsonify({'error': 'All fields are required'}), 400

    if password != confirm_password:
        return jsonify({'error': 'Passwords do not match'}), 400

    hashed_password = generate_password_hash(password)

    try:
        with mysql.connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
            existing_user = cursor.fetchone()

            if existing_user:
                return jsonify({'error': 'Username or email already exists'}), 400

            cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", 
                           (username, email, hashed_password))

            mysql.connection.commit()
            return jsonify({'message': 'User registered successfully'}), 201

    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'error': str(e)}), 500

# 🔹 User Login API
@auth_bp.route('/login', methods=['POST'])
@cross_origin(origin='http://localhost:4200')
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    try:
        with mysql.connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()

            if not user or not check_password_hash(user['password'], password):
                return jsonify({'error': 'Invalid email or password'}), 401

            return jsonify({'message': 'Login successful', 'user': {'id': user['id'], 'username': user['username'], 'email': user['email']}}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 🔹 List All Users API
@auth_bp.route('/users', methods=['GET'])
@cross_origin(origin='http://localhost:4200')
def get_users():
    try:
        with mysql.connection.cursor() as cursor:
            cursor.execute("SELECT id, username, email FROM users")
            users = cursor.fetchall()
            return jsonify({'users': users}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
