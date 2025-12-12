from flask import Blueprint, jsonify, request
from db import mysql
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.pr_product_service import get_client_products

product_bp = Blueprint('product', __name__)

@product_bp.route('/products', methods=['GET'])
def get_products():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT product_id, product_name, category, sale_price, description FROM product ORDER BY product_id;")
        products = cur.fetchall()
        cur.close()
        return jsonify({'status': 'success', 'data': products})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@product_bp.route('/all-products', methods=['GET'])
def get_mas_products():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT product_id, hsn_no, name, unit, unit_cost, client_id FROM products ORDER BY product_id;")
        products = cur.fetchall()
        cur.close()
        return jsonify({'status': 'success', 'data': products})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
@product_bp.route('/products/autocomplete', methods=['GET'])
@jwt_required()
def get_search_products():
    client_id=int(get_jwt_identity())
    search = request.args.get('search', '', type=str)
    results = get_client_products(client_id, search)
    data = [
        {
            "product_id": r.product_id,
            "name": r.name,
            "hsn_no": r.hsn_no
        } for r in results
    ]
    return jsonify(data)