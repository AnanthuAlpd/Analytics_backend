from flask import Blueprint, request, jsonify
from services.leads_service import (
    create_lead, 
    get_leads_dashboard_stats, 
    get_all_leads_service,
    update_lead_service,
    add_lead_note_service,
    get_lead_activities_service
)
from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt
from services.base_service import BaseService
from models.employee import Employee

leads_bp = Blueprint('leads', __name__)

@leads_bp.route('/leads/add', methods=['POST'])
@jwt_required()  
def add_lead():
    data = request.json
    emp_id = get_jwt_identity() 
    result, status_code = create_lead(data, emp_id)
    return jsonify(result), status_code

@leads_bp.route('/leads/activities/add', methods=['POST'])
@jwt_required()
def add_note():
    data = request.json
    current_emp_id = get_jwt_identity()
    
    # Validate input
    if not data.get('lead_id') or not data.get('details'):
        return jsonify({"error": "lead_id and details are required"}), 400
        
    result, status_code = add_lead_note_service(
        lead_id=data['lead_id'],
        emp_id=current_emp_id,
        details=data['details']
    )
    return jsonify(result), status_code

@leads_bp.route('/leads/update/<int:id>', methods=['PUT'])
@jwt_required()
def update_lead(id):
    data = request.json
    current_emp_id = get_jwt_identity()
    result, status_code = update_lead_service(id, data, current_emp_id)
    return jsonify(result), status_code

@leads_bp.route('/leads/<int:id>/activities', methods=['GET'])
@jwt_required()
def get_lead_activities(id):
    result, status_code = get_lead_activities_service(id)
    return jsonify(result), status_code

@leads_bp.route('/leads/get-leads-byEmplId', methods=['GET'])
@jwt_required()
def get_lead_by_employee_id():
    emp_id = get_jwt_identity() 
    result, status_code=get_leads_dashboard_stats(emp_id)
    return jsonify(result),status_code

@leads_bp.route('/leads/getall', methods=['GET'])
@jwt_required()
def get_all_leads():
    try:
        claims = get_jwt()
        if claims.get("user_type") != "EMPLOYEE":
            return BaseService.create_response(message="Access denied.", status="error", code=403)

        user_id = get_jwt_identity()
        user = Employee.query.get(user_id)
        
        if not user:
            return BaseService.create_response(message="User not found", status="error", code=404)
        data = get_all_leads_service()
        return BaseService.create_response(data=data, message="All leads fetched successfully")
    except Exception as e:
        return BaseService.create_response(message=str(e), status="error", code=500)