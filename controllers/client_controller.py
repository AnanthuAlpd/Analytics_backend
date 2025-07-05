# controllers/client_controller.py

from flask import Blueprint, request, jsonify
from services.client_service import get_all_clients, add_client
from models.clients import db

clients_bp = Blueprint('clients', __name__, url_prefix='/api')

@clients_bp.route('/clients', methods=['GET'])
def get_clients():
    clients = get_all_clients()
    return jsonify([client.to_dict() for client in clients]), 200

@clients_bp.route('/add_client', methods=['POST'])
def create_client():
    data = request.get_json()
    required_fields = ['name', 'email']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        client = add_client(data)
        return jsonify(client.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
