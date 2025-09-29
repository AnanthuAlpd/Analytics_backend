from flask import Blueprint, request, jsonify
from services.leads_service import create_lead,get_leads_dashboard_stats,get_all_leads_service
from flask_jwt_extended import get_jwt_identity, jwt_required
from services.base_service import BaseService

leads_bp = Blueprint('leads', __name__)

@leads_bp.route('/leads/add', methods=['POST'])
@jwt_required()  
def add_lead():
    data = request.json
    emp_id = get_jwt_identity() 
    result, status_code = create_lead(data, emp_id)
    return jsonify(result), status_code

@leads_bp.route('/leads/get-leads-byEmplId', methods=['GET'])
@jwt_required()
def get_lead_by_employee_id():
    emp_id = get_jwt_identity() 
    result, status_code=get_leads_dashboard_stats(emp_id)
    return jsonify(result),status_code

@leads_bp.route('/leads/getall', methods=['GET'])
def get_all_leads():
    try:
        data = get_all_leads_service()
        return BaseService.create_response(data=data, message="All leads fetched successfully")
    except Exception as e:
        return BaseService.create_response(message=str(e), status="error", code=500)