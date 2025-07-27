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
            identity=str(employee.id), 
            additional_claims={"user_type": "EMPLOYEE"}
        )
        refresh_token = create_refresh_token(
            identity=str(employee.id),
            #additional_claims={"user_type": "EMPLOYEE"} 
        )

        return jsonify({
            "access_token": access_token,
            "user_type": "EMPLOYEE",
            "employee": employee.to_dict(),
            "refresh_token": refresh_token
        }), 200

    # Try client
    client = Client.query.filter_by(email=email).first()
    if client and client.check_password(password):
        access_token = create_access_token(
            identity=str(client.client_id), 
            additional_claims={"user_type": "CLIENT"}
        )
        refresh_token = create_refresh_token(
            identity=str(client.client_id),
            #additional_claims={"user_type": "CLIENT"}  # ✅ add type claim
        )
        service_name = client.service.name
        return jsonify({
            "access_token": access_token,
            "user_type": "CLIENT",
            "client": {
                "id": client.client_id,
                "name": client.name,
                "email": client.email,
                "service_name":service_name
            },
            "refresh_token": refresh_token
        }), 200

    return jsonify({"message": "Invalid email or password"}), 401

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



