from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.pr_monthly_sales_service import get_april_summary,get_top_10_selling_products,get_top_10_revenue_products,get_least_selling_products,get_unsold_products,get_low_performance_products,get_top_valued_products
pr_sales_dashboard = Blueprint('pr_sales_dashboard', __name__)

@pr_sales_dashboard.route('/sales/summary')
@jwt_required()
def summary(): 
    client_id = int(get_jwt_identity())
    return jsonify(get_april_summary(client_id))

@pr_sales_dashboard.route('/sales/top_10_selling_products')
@jwt_required()
def top_10_selling_products(): 
    client_id = int(get_jwt_identity())
    return jsonify(get_top_10_selling_products(client_id))

@pr_sales_dashboard.route('/sales/top_10_revenue_products')
@jwt_required()
def top_10_revenue_products(): 
    client_id = int(get_jwt_identity())
    return jsonify(get_top_10_revenue_products(client_id))

@pr_sales_dashboard.route('/sales/least_selling_products')
@jwt_required()
def least_selling_products(): 
    client_id = int(get_jwt_identity())
    return jsonify(get_least_selling_products(client_id))

@pr_sales_dashboard.route('/sales/unsold_products')
@jwt_required()
def unsold_products(): 
    client_id = int(get_jwt_identity())
    return jsonify(get_unsold_products(client_id))

@pr_sales_dashboard.route('/sales/low_performance_products')
@jwt_required()
def low_performance_products(): 
    client_id = int(get_jwt_identity())
    return jsonify(get_low_performance_products(client_id))

@pr_sales_dashboard.route('/sales/top_valued_products')
@jwt_required()
def top_valued_products(): 
    client_id = int(get_jwt_identity())
    return jsonify(get_top_valued_products(client_id))

