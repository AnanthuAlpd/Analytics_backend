from flask import Blueprint, request, jsonify
from services.aswims.appointment_service import AppointmentService
from flask_jwt_extended import get_jwt_identity, jwt_required
from services.base_service import BaseService

appointments_bp = Blueprint('appointments', __name__)

@appointments_bp.route('getAllAppointments', methods=['GET'])
def get_appointments():
    try:
        data = AppointmentService.get_all_appointments()
        return BaseService.create_response(
            data=data,
            message="Appointments fetched successfully",
            status="success",
            code=200
        )
    except Exception as e:
        return BaseService.create_response(
            message=str(e),
            status="error",
            code=500
        )