from flask import Blueprint, jsonify
from services.services_service import get_all_services

service_bp = Blueprint('services', __name__)

@service_bp.route('/services', methods=['GET'])
def list_services():
    return jsonify(get_all_services()), 200
