from datetime import datetime, timedelta
import logging
from db import db
from models.leads import Lead
from models.leads_activity_logs import LeadsActivityLog
from models.leads_status import LeadsStatus

# Set up a dedicated logger for the lead updater
logger = logging.getLogger('lead_updater')
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s in tasks.py: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def check_and_update_overdue_leads(app):
    """
    Scheduled task to check for leads whose follow_up_date has passed.
    Changes status to 'Follow-Up' and alerts the user by pushing it into the follow-up queue.
    """
    with app.app_context():
        try:
            current_time = datetime.now()
            logger.info(f"Starting scheduled task to check for overdue leads.")
            
            # Dynamically fetch status IDs
            follow_up_status = LeadsStatus.query.filter_by(status_name='Follow-Up').first()
            # Also fetch statuses we want to ignore (already closed/completed)
            ignore_statuses = LeadsStatus.query.filter(LeadsStatus.status_name.in_(['Converted', 'Dropped', 'Not Interested', 'Invalid'])).all()
            ignore_status_ids = [s.id for s in ignore_statuses]

            if not follow_up_status:
                logger.warning(f"Skipping update task: 'Follow-Up' status not found in DB.")
                return

            # Find all leads where follow_up_date is today or in the past
            # and they are not already in 'Follow-Up' or an ignored status
            overdue_leads = Lead.query.filter(
                Lead.follow_up_date != None,
                Lead.follow_up_date <= current_time,
                Lead.status_id != follow_up_status.id,
                ~Lead.status_id.in_(ignore_status_ids) if ignore_status_ids else True
            ).all()

            updated_count = 0
            for lead in overdue_leads:
                # Update the status
                old_status_obj = LeadsStatus.query.get(lead.status_id) if lead.status_id else None
                old_status_name = old_status_obj.status_name if old_status_obj else "Unknown"

                lead.status_id = follow_up_status.id
                # Note: We intentionally DO NOT update follow_up_date here, so it remains past-due
                # until the user actively logs an action and advances the stage or updates it manually.

                # Create a log for this automated system action
                auto_log = LeadsActivityLog(
                    lead_id=lead.id,
                    emp_id=lead.emp_id, # Reusing the assigned employee
                    action_type='System Notification', # Storing as standard string now
                    details='System auto-flagged lead for Follow-Up: Pipeline scheduled action date has been reached.',
                    old_value=old_status_name,
                    new_value=follow_up_status.status_name
                )
                db.session.add(auto_log)
                updated_count += 1


            
            if updated_count > 0:
                db.session.commit()
                logger.info(f"System successfully changed {updated_count} untouched leads to 'Follow-Up'.")
            else:
                logger.info(f"No leads needed updating right now.")

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error checking overdue leads: {e}")
