from models.aswims.designations import AswimsDesignations

class AppointmentService:
    @staticmethod
    def get_all_appointments():
        # Fetch all appointments ordered by hierarchy level (seniority)
        appointments = AswimsDesignations.query.order_by(AswimsDesignations.hierarchy_level.asc()).all()
        
        # Convert SQLAlchemy objects to a list of dictionaries
        return [
            {
                "id": appt.id,
                "designation_name": appt.designation_name,
                "hierarchy_level": appt.hierarchy_level
            } for appt in appointments
        ]