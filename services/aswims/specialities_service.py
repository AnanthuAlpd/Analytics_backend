from models.aswims.specialities import AswimsSpecialities

def get_all_main_specialities():
    """Fetches all specialities where parent_id is NULL."""
    mains = AswimsSpecialities.query.filter(AswimsSpecialities.parent_id == None).all()
    return [
        {
            "id": spec.id,
            "speciality_name": spec.speciality_name
        } for spec in mains
    ]

def get_super_specialities_by_parent(parent_id):
    """Fetches sub-specialities linked to a specific main speciality."""
    subs = AswimsSpecialities.query.filter_by(parent_id=parent_id).all()
    return [
        {
            "id": spec.id,
            "speciality_name": spec.speciality_name
        } for spec in subs
    ]