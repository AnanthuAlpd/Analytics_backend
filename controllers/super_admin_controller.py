from flask import Blueprint, jsonify,request
from services.department_service import get_all_departments
from services.role_service import get_all_roles
from services.employee_service import update_employee_by_id
from services import department_service,role_service
from services.menu_service import MenuService
from services.base_service import BaseService

super_admin_bp = Blueprint('super_admin', __name__)

@super_admin_bp.route('/departments', methods=['GET'])
def list_departments():
    return jsonify(get_all_departments()), 200
@super_admin_bp.route('/roles',methods=['GET'])
def list_roles():
    return jsonify(get_all_roles()), 200

@super_admin_bp.route('/update-employee/<int:employee_id>', methods=['PUT'])
def update_employee_route(employee_id):
    data = request.get_json()
    response, status_code = update_employee_by_id(employee_id, data)
    return jsonify(response), status_code
@super_admin_bp.route('/departments', methods=['POST'])
def create_department():
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'error': 'Name is required'}), 400

    result = department_service.create_department(data)
    return jsonify(result), 201


@super_admin_bp.route('/departments/<int:department_id>', methods=['PUT'])
def update_department(department_id):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No input data provided'}), 400

    result = department_service.update_department(department_id, data)
    if not result:
        return jsonify({'error': 'Department not found'}), 404

    return jsonify(result), 200

@super_admin_bp.route('/roles', methods=['POST'])
def create_role():
    data = request.json
    new_role = role_service.create_role(data)
    return jsonify(new_role), 201

@super_admin_bp.route('/roles/<int:role_id>', methods=['PUT'])
def update_role(role_id):
    data = request.json
    updated_role = role_service.update_role(role_id, data)
    if updated_role:
        return jsonify(updated_role)
    return jsonify({'message': 'Role not found'}), 404

@super_admin_bp.route('/roles/<int:role_id>', methods=['DELETE'])
def delete_role(role_id):
    success = role_service.delete_role(role_id)
    if success:
        return jsonify({'message': 'Role deleted'})
    return jsonify({'message': 'Role not found'}), 404

@super_admin_bp.route("/menus", methods=["POST"])
def create_menu():
    result = MenuService.create_menu(request.json)
    return BaseService.create_response(
        data=result.get("data"),
        message=result.get("message"),
        status=result.get("status", "success"),
        code=result.get("code", 200),
    )

@super_admin_bp.route("/menus/<int:menu_id>", methods=["PUT"])
def update_menu(menu_id):
    result = MenuService.update_menu(menu_id, request.json)
    return BaseService.create_response(
        data=result.get("data"),
        message=result.get("message"),
        status=result.get("status", "success"),
        code=result.get("code", 200),
    )

@super_admin_bp.route("/menus/<int:menu_id>", methods=["DELETE"])
def delete_menu(menu_id):
    result = MenuService.delete_menu(menu_id)
    return BaseService.create_response(
        message=result.get("message"),
        status=result.get("status", "success"),
        code=result.get("code", 200),
    )