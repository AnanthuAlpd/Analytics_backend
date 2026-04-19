# controllers/employee_controller.py
from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from services.employee_service import get_all_employees, add_employee as add_employee_service, authenticate, delete_employee_by_id
from services.base_service import BaseService

employee_bp = Blueprint('employee', __name__)

@employee_bp.route('/employees', methods=['GET'])
def list_employees():
    return jsonify(get_all_employees()), 200

@employee_bp.route('/add_employee', methods=['POST'])
@cross_origin(origins='http://localhost:4200')
def add_employee():
    data = request.get_json()

    if not data:
        return BaseService.create_response(message="No input data provided", status="error", code=400)

    # Basic validation
    if data.get('password') != data.get('confirm_password'):
        return BaseService.create_response(message="Passwords do not match", status="error", code=400)

    # Delegate to service layer
    success, result = add_employee_service(data)

    if success:
        return BaseService.create_response(data=result, message="Employee added successfully", code=201)
    else:
        # result contains the friendly error message (e.g., "Email already exists")
        code = 409 if "already exists" in result.lower() else 400
        return BaseService.create_response(message=result, status="error", code=code)

@employee_bp.route('/employee_login', methods=['POST'])
@cross_origin(origins='http://localhost:4200')
def login():
    data = request.get_json()

    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400

    email = data['email']
    password = data['password']

    employee = authenticate(email, password)
    if employee:
        return jsonify({
            'message': 'Login successful',
            'employee': employee.to_dict()
        }), 200
    else:
        return jsonify({'error': 'Invalid email or password'}), 401

@employee_bp.route('/delete_employee/<int:employee_id>', methods=['DELETE'])
@cross_origin(origins='http://localhost:4200')
def delete_employee(employee_id):
    response, status_code = delete_employee_by_id(employee_id)
    return jsonify(response), status_code