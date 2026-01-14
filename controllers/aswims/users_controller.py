from flask import Blueprint, request
from services.aswims.user_service import UserService
from services.base_service import BaseService
from flask_jwt_extended import get_jwt, jwt_required

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/users/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Basic validation
        required_fields = ['first_name', 'last_name', 'mob_no', 'password', 'designation_id', 'speciality_id']
        if not all(field in data for field in required_fields):
            return BaseService.create_response(message="Missing required fields", status="error", code=400)

        user = UserService.register_user(data)
        
        return BaseService.create_response(
            message="User registered successfully. Pending approval.",
            status="success",
            code=201
        )
    except ValueError as e:
        return BaseService.create_response(message=str(e), status="error", code=400)
    except Exception as e:
        return BaseService.create_response(message=str(e), status="error", code=500)

@user_bp.route('/users/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        identifier = data.get('identifier') # Matches your login form input
        password = data.get('password')

        if not identifier or not password:
            return BaseService.create_response(
                message="Missing credentials", 
                status="error", 
                code=400
            )

        result = UserService.login_user(identifier, password)
        
        return BaseService.create_response(
            data=result,
            message="Login successful",
            status="success",
            code=200
        )
    except ValueError as e:
        return BaseService.create_response(message=str(e), status="error", code=401)
    except Exception as e:
        return BaseService.create_response(message=str(e), status="error", code=500)

@user_bp.route('/users/getAllusers', methods=['GET'])
def get_users():
    try:
        data = UserService.get_all_users()
        return BaseService.create_response(data=data, message="Users fetched successfully")
    except Exception as e:
        # This catches the Exception raised by the service above
        return BaseService.create_response(message=str(e), status="error", code=500)


@user_bp.route('/update-status', methods=['POST'])
@jwt_required()
def update_status():
    # Only allow users with high hierarchy level to approve
    claims = get_jwt()
    if claims.get("h_level", 99) > 10:
        return BaseService.create_response(message="Unauthorized", status="error", code=403)

    data = request.get_json()
    user_id = data.get('userId')
    status = data.get('status')

    result = UserService.update_user_status(user_id, status)
    if result["success"]:
        return BaseService.create_response(message=result["message"])
    return BaseService.create_response(message=result["message"], status="error", code=400)


# @user_bp.route('/update-status', methods=['POST'])
# def update_status():
#     # DEBUG 1: Print the raw Authorization header to check for hidden quotes or spaces
#     print(f"RAW HEADER: '{request.headers.get('Authorization')}'")

#     @jwt_required()
#     def protected_logic():
#         claims = get_jwt()
        
#         # DEBUG 2: Print the claims to verify h_level type and value
#         print(f"JWT CLAIMS: {claims}")
        
#         user_h_level = claims.get("h_level", 99)
#         print(f"USER H_LEVEL: {user_h_level} (Type: {type(user_h_level)})")

#         if user_h_level > 10:
#             return BaseService.create_response(
#                 message=f"Unauthorized: Level {user_h_level} too low", 
#                 status="error", 
#                 code=403
#             )