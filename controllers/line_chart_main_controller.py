from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from services.sales_service import SalesService
from services.revenue_service import get_monthly_revenue_comparison

sales_chart_bp = Blueprint('sales_chart', __name__)

@sales_chart_bp.route('/sales-chart', methods=['GET'])
@cross_origin(origin='http://localhost:4200')
def get_sales_chart_route():
    try:
        product_id = request.args.get('product_id', type=int)
        months = request.args.get('months', type=int)  

        data = SalesService.get_monthly_comparison(product_id, months)
        return jsonify({'status': 'success','data':data})
    except Exception as e:
        return jsonify({'status':'error','message':str(e)}),500

@sales_chart_bp.route('/sales-table',methods=['GET'])
@cross_origin(origin='http://localhost:4200')
def get_sales_table_route():
    try:
        data = SalesService.get_sales_comparison_table()
        return jsonify({"status": "success", "data": data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    
@sales_chart_bp.route('/revenue-chart',methods=['GET'])
@cross_origin(origin='http://localhost:4200')
def get_revenue_chart():
    try:
        data = get_monthly_revenue_comparison()
        return jsonify({"status": "success", "data": data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
