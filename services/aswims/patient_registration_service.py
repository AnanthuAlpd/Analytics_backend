from datetime import datetime
from models.aswims.patients import AswimsPatient, db
from models.aswims.wards import AswimsWard

from services.base_service import BaseService  # Import your BaseService

class PatientRegistrationService(BaseService): # Inherit if you have shared logic
    
    @staticmethod
    def get_ward_list():
        try:
            wards = AswimsWard.query.filter_by(is_active=True).all()
            ward_data = [{"id": w.id, "ward_name": w.ward_name} for w in wards]
            return BaseService.create_response(data=ward_data)
        except Exception as e:
            return BaseService.create_response(message=str(e), status="error", code=500)

    @staticmethod
    def register_new_admission(data, staff_id):
        try:
            # Basic validation
            if not data.get('name') or not data.get('ward_id'):
                return BaseService.create_response(message="Missing required patient fields", status="error", code=400)

            # Parse Date
            doa_str = data.get('doa').replace('Z', '')
            parsed_doa = datetime.fromisoformat(doa_str)

            new_patient = AswimsPatient(
                name=data['name'],
                ward_id=data['ward_id'],
                bed_no=data['bed_no'],
                diagnosis=data['diagnosis'],
                doa=parsed_doa,
                created_by=staff_id
            )

            db.session.add(new_patient)
            db.session.commit()
            
            return BaseService.create_response(message="Patient admission recorded successfully", code=201)
            
        except Exception as e:
            db.session.rollback()
            return BaseService.create_response(message=f"Database Error: {str(e)}", status="error", code=500)

    
    @staticmethod
    def get_patients_by_ward(ward_id):
        try:
            # Fetch only patients who are currently 'Admitted' in the specific ward
            patients = AswimsPatient.query.filter_by(
                ward_id=ward_id, 
                status='Admitted'
            ).order_by(AswimsPatient.doa.desc()).all()

            # Convert to list of dictionaries using the model's to_dict method
            patient_list = [p.to_dict() for p in patients]
            
            return BaseService.create_response(
                data=patient_list, 
                message=f"Fetched {len(patient_list)} patients", 
                status="success", 
                code=200
            )
        except Exception as e:
            return BaseService.create_response(
                message=f"Error fetching ward data: {str(e)}", 
                status="error", 
                code=500
            )