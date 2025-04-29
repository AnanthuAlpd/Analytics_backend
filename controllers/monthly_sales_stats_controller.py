from flask import Blueprint, jsonify
from flask_cors import cross_origin
from services.monthly_sales_stats_service import get_monthly_totals_service

monthly_stats_bp = Blueprint('monthly_stats', __name__)

@monthly_stats_bp.route('/monthly-totals', methods=['GET'])
@cross_origin(origin='http://localhost:4200')
def get_monthly_totals():
    response, status = get_monthly_totals_service()
    return jsonify(response), status
