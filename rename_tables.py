from app import create_app
from db import db
from sqlalchemy import text

app = create_app()

queries = [
    "RENAME TABLE lead_status TO leads_status;",
    "RENAME TABLE lead_stage TO leads_stage;",
    "RENAME TABLE lead_sources TO leads_sources;",
    "RENAME TABLE stage_actions TO leads_stage_actions;",
    "RENAME TABLE activity_type TO leads_activity_type;",
    "RENAME TABLE lead_activity_logs TO leads_activity_logs;"
]

def rename_tables():
    with app.app_context():
        # Temporarily disable foreign key checks to allow table renaming
        db.session.execute(text("SET FOREIGN_KEY_CHECKS=0;"))
        for query in queries:
            try:
                db.session.execute(text(query))
                print(f"Executed: {query}")
            except Exception as e:
                print(f"Failed to execute '{query}': {str(e)}")
        
        # Re-enable foreign key checks
        db.session.execute(text("SET FOREIGN_KEY_CHECKS=1;"))
        db.session.commit()
        print("Database tables successfully renamed.")

if __name__ == '__main__':
    rename_tables()
