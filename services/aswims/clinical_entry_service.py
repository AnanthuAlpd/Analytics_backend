from models.aswims.patient_medicines import PatientMedicine
from models.aswims.medicine_categories import MedicineCategory
from models.aswims.medicine_frequencies import MedicineFrequency
from db import db
from models.aswims.patient_vitals import AswimsPatientVitals
from models.aswims.clinical_entries import AswimsClinicalEntry
from services.base_service import BaseService
from datetime import datetime

class ClinicalService(BaseService):

    @staticmethod
    def save_unified_entry(data, staff_id):
        """
        Saves unified clinical data: Vitals, Clinical Notes, and Multiple Medications.
        """
        try:
            if data.get('mode') == 'vitals-only':
                # 1. Save Vitals Data (Always created in both modes)
                new_vitals = AswimsPatientVitals(
                    patient_id=data.get('patient_id'),
                    temp=data.get('temp'),
                    pulse=data.get('pulse'),
                    bp=data.get('bp'),
                    spo2=data.get('spo2'),
                    created_by=staff_id
                    # timestamps are handled by server_default in our model
                )
                db.session.add(new_vitals)

            # 2. Save Clinical Progress Note (Full Mode)
            if data.get('mode') == 'full' or data.get('daily_notes'):
                new_clinical = AswimsClinicalEntry(
                    patient_id=data.get('patient_id'),
                    daily_notes=data.get('daily_notes'),
                    created_by=staff_id,
                    entry_date=datetime.now()
                )
                db.session.add(new_clinical)

            # 3. Handle Multiple Medications (Array of Objects)
            medicines_list = data.get('medicines', [])
            if medicines_list:
                for med in medicines_list:
                    new_medication = PatientMedicine(
                        patient_id=data.get('patient_id'),
                        category_id=med.get('category_id'),
                        frequency_id=med.get('frequency_id'),
                        medicine_name=med.get('medicine_name'),
                        dose=med.get('dose'),
                        daily_count=med.get('daily_count'),
                        remarks=med.get('remarks'),
                        created_by=staff_id
                    )
                    db.session.add(new_medication)

            # 4. Commit everything together
            db.session.commit()

            return BaseService.create_response(
                message="Clinical record and medications saved successfully",
                status="success",
                code=201
            )

        except Exception as e:
            db.session.rollback()
            return BaseService.create_response(
                message=f"Database Error: {str(e)}",
                status="error",
                code=500
            )

    @staticmethod
    def get_patient_history(patient_id):
        """
        Retrieves combined history of vitals and notes for a specific patient.
        """
        try:
            # You can expand this later to fetch data for clinical charts
            vitals = AswimsPatientVitals.query.filter_by(patient_id=patient_id).all()
            notes = AswimsClinicalEntry.query.filter_by(patient_id=patient_id).all()
            
            return BaseService.create_response(
                data={
                    "vitals": [v.to_dict() for v in vitals],
                    "notes": [n.to_dict() for n in notes]
                },
                status="success",
                code=200
            )
        except Exception as e:
            return BaseService.create_response(
                message=str(e),
                status="error",
                code=500
            )

    @staticmethod
    def get_med_frequencies():
        """
        Retrieves combined history of vitals and notes for a specific patient.
        """
        try:
            # You can expand this later to fetch data for clinical charts
            frequencies = MedicineFrequency.query.all()

            return BaseService.create_response(
                data={
                    "med_frequencies": [v.to_dict() for v in frequencies]
                },
                status="success",
                code=200
            )
        except Exception as e:
            return BaseService.create_response(
                message=str(e),
                status="error",
                code=500
            )

    @staticmethod
    def get_med_categories():
        """
        Retrieves combined history of vitals and notes for a specific patient.
        """
        try:
            # You can expand this later to fetch data for clinical charts
            categories = MedicineCategory.query.all()

            return BaseService.create_response(
                data={
                    "med_categories": [v.to_dict() for v in categories]
                },
                status="success",
                code=200
            )
        except Exception as e:
            return BaseService.create_response(
                message=str(e),
                status="error",
                code=500
            )