from flask import Blueprint
from services.aswims.specialities_service import get_all_main_specialities, get_super_specialities_by_parent
from services.base_service import BaseService

speciality_bp = Blueprint('speciality_bp', __name__)

@speciality_bp.route('/getMainSpecialities', methods=['GET'])
def get_main_specs():
    try:
        data = get_all_main_specialities()
        return BaseService.create_response(
            data=data,
            message="Main specialities fetched successfully",
            code=200
        )
    except Exception as e:
        return BaseService.create_response(message=str(e), status="error", code=500)

@speciality_bp.route('/getSuperSpecialities/<int:parent_id>', methods=['GET'])
def get_super_specs(parent_id):
    try:
        data = get_super_specialities_by_parent(parent_id)
        return BaseService.create_response(
            data=data,
            message=f"Super specialities for parent {parent_id} fetched",
            code=200
        )
    except Exception as e:
        return BaseService.create_response(message=str(e), status="error", code=500)