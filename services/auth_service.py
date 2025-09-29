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
