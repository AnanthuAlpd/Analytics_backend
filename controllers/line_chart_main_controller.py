from flask import Blueprint, jsonify
from flask_cors import cross_origin
from services.line_chart_main_service import get_sales_chart as get_sales_chart_service
from services.sales_service import SalesService

sales_chart_bp = Blueprint('sales_chart', __name__)

@sales_chart_bp.route('/sales-chart', methods=['GET'])
@cross_origin(origin='http://localhost:4200')
def get_sales_chart_route():
    try:
        data = SalesService.get_monthly_comparison()
        return jsonify({'status': 'success','data':data})
    except Exception as e:
        return jsonify({'status':'error','message':str(e)}),500
