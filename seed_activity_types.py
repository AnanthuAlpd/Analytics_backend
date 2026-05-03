from app import create_app
from db import db
from models.leads_activity_type import LeadsActivityType

activity_names = ['Lead Created', 'Stage Progressed', 'Status Change', 'Call Connected', 'Left Voicemail', 'Sent Message', 'Meeting Scheduled', 'Other']

app = create_app()

def seed():
    with app.app_context():
        for name in activity_names:
            if not LeadsActivityType.query.filter_by(name=name).first():
                print(f"Adding activity type: {name}")
                at = LeadsActivityType(name=name)
                db.session.add(at)
        db.session.commit()
        print("Activity types successfully seeded.")

if __name__ == '__main__':
    seed()
