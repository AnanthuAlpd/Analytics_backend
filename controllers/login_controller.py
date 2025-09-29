from flask import request, jsonify,Blueprint
from models.employee import Employee
from models.clients import Client
from sqlalchemy import union_all, literal
from flask_jwt_extended import create_access_token, create_refresh_token,jwt_required,get_jwt_identity,get_jwt
from db import db
from services.auth_service import AuthService
from services.menu_service import MenuService

login_bp = Blueprint('login', __name__)

@login_bp.route('/login_new', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return AuthService.create_response(message="Invalid JSON", status="error", code=400)

        email = data.get('email', '').strip()
        password = data.get('password', '').strip()

        if not email or not password:
            return AuthService.create_response(message="Email and password are required", status="error", code=400)

        return AuthService.login_user(email, password)

    except Exception as e:
        print(f"Login error: {str(e)}")
        return AuthService.create_response(message="Login failed. Please try again.", status="error", code=500)

@login_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()  # this is employee.id or client.client_id
    claims = get_jwt()

    # Fetch user_type from DB instead
    user_type = "UNKNOWN"
    if Employee.query.get(identity):
        user_type = "EMPLOYEE"
    elif Client.query.get(identity):
        user_type = "CLIENT"

    new_token = create_access_token(
        identity=identity,
        additional_claims={"user_type": user_type}
    )

    return jsonify(access_token=new_token), 200

@login_bp.route('/get-menus', methods=['GET'])
def menus_with_roles():
    menus = MenuService.get_all_menus_with_roles()
    return jsonify(menus)

@login_bp.route('/get-menus-by-ids', methods=['POST'])
def get_menus_with_roles():
    data = request.get_json()
    role_ids = data.get("role_ids", [])
    menus = MenuService.get_menus_by_roles(role_ids)
    return jsonify(menus)



