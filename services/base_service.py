from flask_jwt_extended import create_access_token, create_refresh_token
from datetime import timedelta
from flask import jsonify

class BaseService:
    @staticmethod
    def create_response(data=None, message=None, status="success", code=200):
        response = {"status": status, "message": message}
        if data:
            response["data"] = data
        return jsonify(response), code

    @staticmethod
    def generate_tokens(identity, user_type):
        access_token = create_access_token(
            identity=str(identity),
            additional_claims={"user_type": user_type},
            expires_delta=timedelta(minutes=15)
        )
        refresh_token = create_refresh_token(
            identity=str(identity),
            expires_delta=timedelta(days=30)
        )
        return access_token, refresh_token