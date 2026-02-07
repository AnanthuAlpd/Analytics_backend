from sqlalchemy import literal
from sqlalchemy.sql import union_all
from flask import request
from models.clients import Client
from models.employee import Employee
from db import db
from .base_service import BaseService

class AuthService(BaseService):

    @staticmethod
    def login_user(email, password):
        # Query both tables
        employee_subquery = db.session.query(
            Employee.id.label('user_id'),
            Employee.email,
            Employee.password,
            literal('EMPLOYEE').label('user_type')
        ).filter_by(email=email)

        client_subquery = db.session.query(
            Client.client_id.label('user_id'),
            Client.email,
            Client.password,
            literal('CLIENT').label('user_type')
        ).filter_by(email=email)

        user_record = db.session.execute(union_all(employee_subquery, client_subquery)).first()
        if not user_record:
            return BaseService.create_response(message="Invalid email or password", status="error", code=401)

        # EMPLOYEE
        if user_record.user_type == 'EMPLOYEE':
            user = Employee.query.options(
                db.joinedload(Employee.department),
                db.joinedload(Employee.roles)
            ).get(user_record.user_id)

            if not user or not user.check_password(password):
                return BaseService.create_response(message="Invalid email or password", status="error", code=401)

            access_token, refresh_token = BaseService.generate_tokens(user.id, "EMPLOYEE")
            return BaseService.create_response(
                data={
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user_type": "EMPLOYEE",
                    "user": user.to_dict()
                },
                message="Login successful"
            )

        # CLIENT
        elif user_record.user_type == 'CLIENT':
            user = Client.query.options(
                db.joinedload(Client.service)
            ).get(user_record.user_id)

            if not user or not user.check_password(password):
                return BaseService.create_response(message="Invalid email or password", status="error", code=401)

            access_token, refresh_token = BaseService.generate_tokens(user.client_id, "CLIENT")
            return BaseService.create_response(
                data={
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user_type": "CLIENT",
                    "user": {
                        "id": user.client_id,
                        "name": user.name,
                        "email": user.email,
                        "service_name": user.service.name
                    }
                },
                message="Login successful"
            )

    @staticmethod
    def verify_identity(email, input_mobile):
        # ... (User lookup logic remains the same) ...
        user_record = AuthService._find_user_record_by_email(email)

        if not user_record:
            # RETURN DICT DIRECTLY
            return {"message": "User not found", "status": "error", "code": 404}

        user = AuthService._get_user_instance(user_record)
        if not user:
             return {"message": "User instance error", "status": "error", "code": 500}

        db_mobile = None
        if user_record.user_type == 'EMPLOYEE':
            db_mobile = user.mob_no
        elif user_record.user_type == 'CLIENT':
            db_mobile = user.phone
            
        if db_mobile and str(db_mobile).strip() == str(input_mobile).strip():
             return {"message": "Identity verified", "status": "success", "code": 200}
        else:
             return {"message": "Email and Mobile number do not match", "status": "error", "code": 400}

    # ---------------------------------------------------------
    # MODIFIED: Returns a Dictionary, NOT a Response Object
    # ---------------------------------------------------------
    @staticmethod
    def reset_password(email, new_password):
        user_record = AuthService._find_user_record_by_email(email)
        
        if not user_record:
            return {"message": "User not found", "status": "error", "code": 404}

        user = AuthService._get_user_instance(user_record)
        
        # ... (Password setting logic remains the same) ...
        user.set_password(new_password)
        
        try:
            db.session.commit()
            return {"message": "Password updated successfully", "status": "success", "code": 200}
        except Exception as e:
            db.session.rollback()
            return {"message": str(e), "status": "error", "code": 500}

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------
    @staticmethod
    def _find_user_record_by_email(email):
        # Union query to find where the email exists
        employee_subquery = db.session.query(
            Employee.id.label('user_id'),
            literal('EMPLOYEE').label('user_type')
        ).filter_by(email=email)

        client_subquery = db.session.query(
            Client.client_id.label('user_id'),
            literal('CLIENT').label('user_type')
        ).filter_by(email=email)

        return db.session.execute(union_all(employee_subquery, client_subquery)).first()

    @staticmethod
    def _get_user_instance(user_record):
        if user_record.user_type == 'EMPLOYEE':
            return Employee.query.get(user_record.user_id)
        elif user_record.user_type == 'CLIENT':
            return Client.query.get(user_record.user_id)
        return None
