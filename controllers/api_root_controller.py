from flask import Blueprint, jsonify

api_root_bp = Blueprint('api_root', __name__)

@api_root_bp.route('/api', methods=['GET'])
def api_root():
    return jsonify({
        "message": "API Root",
        "endpoints": [
            "/api/users",
            "/api/products",
            "/api/sales"
        ]
    })
