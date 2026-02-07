from models.services import Service

def get_all_services():

    services=Service.query.all()

    result=[
        {
            'id':d.id,
            'name':d.name
        }
        for d in services
    ]
    return result