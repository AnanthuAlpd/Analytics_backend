from models.department import Department

def get_all_departments():

    departments=Department.query.all()

    result=[
        {
            'id':d.id,
            'name':d.name
        }
        for d in departments
    ]
    return result