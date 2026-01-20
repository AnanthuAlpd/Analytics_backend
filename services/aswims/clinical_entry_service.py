from db import db
from models.aswims.patient_vitals import AswimsPatientVitals
from models.aswims.clinical_entries import AswimsClinicalEntry
from services.base_service import BaseService
from datetime import datetime

class ClinicalService(BaseService):

    @staticmethod
    def save_unified_entry(data, staff_id):
        """
        Splits and saves unified clinical data into Vitals and Clinical Entry tables.
        """
        try:
            # 1. Prepare Vitals Data
            new_vitals = AswimsPatientVitals(
                patient_id=data.get('patient_id'),
                temp=data.get('temp'),
                pulse=data.get('pulse'),
                bp=data.get('bp'),
                spo2=data.get('spo2'),
                recorded_at=datetime.now(),
                created_by=staff_id
            )
            db.session.add(new_vitals)

            # 2. Check if we need to save a Clinical Progress Note
            # We save this if the mode is 'full' or if daily_notes were provided
            if data.get('mode') == 'full' or data.get('daily_notes'):
                new_clinical = AswimsClinicalEntry(
                    patient_id=data.get('patient_id'),
                    daily_notes=data.get('daily_notes'),
                    entry_date=datetime.now(),
                    created_by=staff_id
                )
                db.session.add(new_clinical)

            # Commit both operations together
            db.session.commit()

            return BaseService.create_response(
                message="Clinical record saved successfully",
                status="success",
                code=201
)
        except Exception as e:
            db.session.rollback()
            return BaseService.create_response(
                message=str(e),
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