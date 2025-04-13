from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from services.user_service import register_user, login_user

user_bp = Blueprint('user', __name__)

@user_bp.route('/register', methods=['POST'])
@cross_origin(origin='http://localhost:4200')
def register():
    data = request.json
    response, code = register_user(
        data.get('username'),
        data.get('email'),
        data.get('password'),
        data.get('confirm_password')
    )
    return jsonify(response), code

@user_bp.route('/login', methods=['POST'])
@cross_origin(origin='http://localhost:4200')
def login():
    data = request.json
    response, code = login_user(data.get('email'), data.get('password'))
    return jsonify(response), code

@user_bp.route('/users', methods=['GET'])
@cross_origin(origin='http://localhost:4200')
def get_users():
    from services.user_service import get_all_users
    response, code = get_all_users()
    return jsonify(response), code
