from flask import Blueprint, jsonify
from db import mysql

product_bp = Blueprint('product', __name__)

@product_bp.route('/products', methods=['GET'])
def get_products():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT product_id, product_name, category, price, description FROM product ORDER BY product_id;")
        products = cur.fetchall()
        cur.close()
        return jsonify({'status': 'success', 'data': products})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
