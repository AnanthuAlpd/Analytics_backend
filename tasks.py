from datetime import datetime, timedelta
import logging
from db import db
from models.leads import Lead
from models.lead_activity_logs import LeadActivityLog
from models.lead_status import LeadStatus

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
    Scheduled task to check for leads created over 3 days ago with no follow_up_date
    and zero follow-up activity logs. Changes status to 'Follow-Up' and sets the follow_up_date.
    """
    with app.app_context():
        try:
            current_time = datetime.now()
            logger.info(f"Starting scheduled task to check for overdue leads.")
            
            # Dynamically fetch status IDs
            new_status = LeadStatus.query.filter_by(status_name='New').first()
            follow_up_status = LeadStatus.query.filter_by(status_name='Follow-Up').first()

            if not new_status or not follow_up_status:
                logger.warning(f"Skipping update task: 'New' or 'Follow-Up' statuses not found in DB.")
                return

            three_days_ago = current_time - timedelta(days=3)

            # Find all leads created over 3 days ago where follow_up_date is NULL and status is 'New'
            overdue_leads = Lead.query.filter(
                Lead.follow_up_date.is_(None),
                Lead.created_at <= three_days_ago,
                Lead.status_id == new_status.id
            ).all()

            updated_count = 0
            for lead in overdue_leads:
                # Query activities excluding 'Lead Created' to see if there was any real follow-up
                activity_count = LeadActivityLog.query.filter(
                    LeadActivityLog.lead_id == lead.id,
                    LeadActivityLog.action_type != 'Lead Created'
                ).count()

                if activity_count == 0:
                    # Update the status and add the current date to follow_up_date
                    lead.status_id = follow_up_status.id
                    lead.follow_up_date = current_time

                    # Create a log for this automated action
                    auto_log = LeadActivityLog(
                        lead_id=lead.id,
                        emp_id=lead.emp_id, # Reusing the assigned employee
                        action_type='Status Change',
                        details='System auto-updated status to Follow-Up and set follow up date due to inactivity.',
                        old_value=new_status.status_name,
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
