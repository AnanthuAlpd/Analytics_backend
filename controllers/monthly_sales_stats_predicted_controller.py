from flask import Blueprint, jsonify
from flask_cors import cross_origin
from services.monthly_sales_stats_predicted_service import get_predicted_monthly_totals_service

monthly_stats_predicted_bp = Blueprint('monthly_stats_predicted', __name__)

@monthly_stats_predicted_bp.route('/predicted-monthly-totals', methods=['GET'])
@cross_origin(origin='http://localhost:4200')
def get_predicted_monthly_totals():
    response, status = get_predicted_monthly_totals_service()
    return jsonify(response), status
