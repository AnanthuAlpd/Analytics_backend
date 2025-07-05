from flask import request, jsonify,Blueprint
from models.employee import Employee
from models.clients import Client
from flask_jwt_extended import create_access_token, create_refresh_token,jwt_required,get_jwt_identity,get_jwt

login_bp = Blueprint('login', __name__)

@login_bp.route('/login_new', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()

    # Try employee
    employee = Employee.query.filter_by(email=email).first()
    if employee and employee.check_password(password):
        access_token = create_access_token(
            identity=str(employee.id),  # identity must be string
            additional_claims={"type": "EMPLOYEE"}
        )
        refresh_token = create_refresh_token(identity=str(employee.id))
        return jsonify({
            "access_token": access_token,
            "user_type": "EMPLOYEE",
            "employee": {
                "id": employee.id,
                "name": employee.name,
                "email": employee.email
            },
            "refresh_token": refresh_token
        }), 200

    # Try client
    client = Client.query.filter_by(email=email).first()
    if client and client.check_password(password):
        access_token = create_access_token(
            identity=str(client.client_id),  # identity must be string
            additional_claims={"type": "CLIENT"}
        )
        refresh_token = create_refresh_token(identity=str(client.client_id))
        return jsonify({
            "access_token": access_token,
            "user_type": "CLIENT",
            "client": {
                "id": client.client_id,
                "name": client.name,
                "email": client.email
            },
            "refresh_token": refresh_token
        }), 200

    return jsonify({"message": "Invalid email or password"}), 401

@login_bp.route('/refresh', methods=['POST'])

@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()  # This is the user ID as string
    claims = get_jwt()             # This gives you the full token payload
    user_type = claims.get("type")  # Either "CLIENT" or "EMPLOYEE"

    if user_type not in {"CLIENT", "EMPLOYEE"}:
        return jsonify({"msg": "Invalid user type in token"}), 400

    new_token = create_access_token(
        identity=identity,
        additional_claims={"type": user_type}
    )

    return jsonify(access_token=new_token), 200


