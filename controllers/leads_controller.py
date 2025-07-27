from flask import Blueprint, request, jsonify
from services.leads_service import create_lead,get_leads_dashboard_stats
from flask_jwt_extended import get_jwt_identity, jwt_required  # If you're using JWT

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