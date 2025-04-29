from flask import jsonify
from models.line_chart_main_model import SalesChart

def get_sales_chart():
    try:
        data = SalesChart.get_sales_data()
        return (data), 200
    except Exception as e:
        return ({"error": str(e)}), 500
