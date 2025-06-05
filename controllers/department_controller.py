from flask import Blueprint, jsonify
from services.department_service import get_all_departments

department_bp = Blueprint('department', __name__)

@department_bp.route('/departments', methods=['GET'])
def list_departments():
    return jsonify(get_all_departments()), 200
