# controllers/client_controller.py

from flask import Blueprint, request, jsonify
from services.client_service import get_all_clients, add_client, delete_client_by_id
from services.base_service import BaseService
from models.clients import db

clients_bp = Blueprint('clients', __name__, url_prefix='/api')

@clients_bp.route('/clients', methods=['GET'])
def get_clients():
    clients = get_all_clients()
    return jsonify([client.to_dict() for client in clients]), 200

@clients_bp.route('/add_client', methods=['POST'])
def create_client():
    data = request.get_json()
    if not data:
        return BaseService.create_response(message="No input data provided", status="error", code=400)

    # Delegate to service layer
    success, result = add_client(data)

    if success:
        return BaseService.create_response(data=result.to_dict(), message="Client added successfully", code=201)
    else:
        # result contains the friendly error message
        code = 409 if "already exists" in result.lower() else 400
        return BaseService.create_response(message=result, status="error", code=code)

@clients_bp.route('/delete_client/<int:client_id>', methods=['DELETE'])
def delete_client(client_id):
    response, status_code = delete_client_by_id(client_id)
    return jsonify(response), status_code
