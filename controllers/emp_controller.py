# controllers/employee_controller.py
from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from services.employee_service import get_all_employees,add_employee as add_employee_service

employee_bp = Blueprint('employee', __name__)

@employee_bp.route('/employees', methods=['GET'])
def list_employees():
    return jsonify(get_all_employees()), 200

@employee_bp.route('/add_employee', methods=['POST'])
@cross_origin(origins='http://localhost:4200')
def add_employee():
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No input data provided'}), 400

    # Basic validation
    if data.get('password') != data.get('confirm_password'):
        return jsonify({'error': 'Passwords do not match'}), 400

    # Delegate to service layer
    success, result = add_employee_service(data)

    if success:
        return jsonify({'message': 'Employee added successfully', 'employee': result}), 201
    else:
        return jsonify({'error': result}), 500