from flask import Blueprint, request, jsonify
from services.aswims.patient_registration_service import PatientRegistrationService
from services.base_service import BaseService
from flask_jwt_extended import get_jwt, jwt_required,get_jwt_identity
from services.aswims.clinical_entry_service import ClinicalService

patient_bp = Blueprint('patient_bp', __name__)

@patient_bp.route('/wards', methods=['GET'])
@jwt_required()
def get_wards():
    # Returns the standardized response from BaseService
    return PatientRegistrationService.get_ward_list()

@patient_bp.route('/register', methods=['POST'])
@jwt_required()
def register_patient():
    staff_id = get_jwt_identity()
    data = request.get_json()
    
    return PatientRegistrationService.register_new_admission(data, staff_id)

@patient_bp.route('/patients/ward/<int:ward_id>', methods=['GET'])
@jwt_required()
def get_patients_by_ward(ward_id):
    """
    Fetch all active patients for a specific ward.
    Standardized via BaseService.
    """
    return PatientRegistrationService.get_patients_by_ward(ward_id)

@patient_bp.route('/get_patient_by_id/<int:patient_id>', methods=['GET'])
# @jwt_required()
def get_patients_by_id(patient_id):
    """
    Fetch all active patients for a specific ward.
    Standardized via BaseService.
    """
    return PatientRegistrationService.get_patients_by_id(patient_id)


# controllers/aswims/patient_controller.py

@patient_bp.route('/clinical-entry', methods=['POST'])
@jwt_required()
def add_clinical_entry():
    try:
        staff_id = get_jwt_identity()
        data = request.get_json()

        if not data:
            return BaseService.create_response(
                message="No input data provided",
                status="error",
                code=400
            )

        # Service already returns (Response, status_code)
        return ClinicalService.save_unified_entry(data, staff_id)

    except Exception as e:
        print(f"Controller Error: {str(e)}")
        return BaseService.create_response(
            message="An unexpected server error occurred",
            status="error",
            code=500
        )

@patient_bp.route('/patients/<int:patient_id>/history', methods=['GET'])
@jwt_required()
def get_patient_clinical_history(patient_id):
    """
    Fetches patient history using standardized BaseService formatting.
    """
    return ClinicalService.get_patient_history(patient_id)

@patient_bp.route('/med-frequencies',methods=['GET'])
def get_all_med_frequencies():
    return ClinicalService.get_med_frequencies()

@patient_bp.route('/med-categories',methods=['GET'])
def get_all_med_categories():
    return ClinicalService.get_med_categories()