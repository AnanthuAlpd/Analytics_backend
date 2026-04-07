from datetime import datetime, timedelta
from sqlalchemy import func, extract
from db import db
from models.leads import Lead
from models.lead_activity_logs import LeadActivityLog

def create_lead(data, emp_id):
    try:
        lead = Lead(
            emp_id=emp_id,
            name=data.get('name'),
            lead_cat=data.get('lead_cat'),
            email=data.get('email'),
            mob_no=data.get('mob_no'),
            lead_source=data.get('lead_source'),
            status=data.get('status', 'New'),  # fallback to 'New' if not provided
            remarks=data.get('remarks')
        )
        db.session.add(lead)
        db.session.commit()
        
        # Log activity
        log_lead_activity(lead.id, emp_id, 'Lead Created', 'Lead was successfully added.')
        
        return {"message": "Lead created successfully", "lead_id": lead.id}, 201

    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500

def get_leads_dashboard_stats(emp_id=None):
    try:
        now = datetime.now()
        current_month = now.month
        previous_month = (now - timedelta(days=30)).month  # Approximation

        # Base query
        base_query = db.session.query(Lead).filter(Lead.emp_id == emp_id)

        # Total leads
        total_client_leads = base_query.filter(Lead.lead_cat == 'Client').count()
        total_employee_leads = base_query.filter(Lead.lead_cat == 'Employee').count()

        # Month-wise leads
        client_current = base_query.filter(
            Lead.lead_cat == 'Client',
            extract('month', Lead.created_at) == current_month
        ).count()

        client_previous = base_query.filter(
            Lead.lead_cat == 'Client',
            extract('month', Lead.created_at) == previous_month
        ).count()

        employee_current = base_query.filter(
            Lead.lead_cat == 'Employee',
            extract('month', Lead.created_at) == current_month
        ).count()

        employee_previous = base_query.filter(
            Lead.lead_cat == 'Employee',
            extract('month', Lead.created_at) == previous_month
        ).count()

        # 🔸 Leads assigned to this employee (emp_id)
        emp_leads = []
        if emp_id:
            emp_leads_query = db.session.query(
                Lead.id,
                Lead.name,
                Lead.email,
                Lead.mob_no,
                Lead.created_at,
                Lead.lead_cat,
                Lead.status
            ).filter(Lead.emp_id == emp_id).all()

            # Convert to list of dicts
            emp_leads = [
                {
                    "id": lead.id,
                    "name": lead.name,
                    "email": lead.email,
                    "mob_no": lead.mob_no,
                    "created_at": lead.created_at.strftime('%Y-%m-%d'),
                    "lead_cat": lead.lead_cat,
                    "status": lead.status
                }
                for lead in emp_leads_query
            ]

        return {
            "total_client_leads": total_client_leads,
            "total_employee_leads": total_employee_leads,
            "client_current": client_current,
            "client_previous": client_previous,
            "employee_current": employee_current,
            "employee_previous": employee_previous,
            "assigned_leads": emp_leads,
            "message": "Dashboard data fetched successfully"
        }, 200

    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500

def get_all_leads_service():
    try:
        leads = Lead.query.all()
        lead_list = [
            {
                "id": lead.id,
                "emp_id": lead.emp_id,
                "emp_name": lead.employee.name if lead.employee else "Unknown",
                "name": lead.name,
                "lead_cat": lead.lead_cat,
                "email": lead.email,
                "mob_no": lead.mob_no,
                "lead_source": lead.lead_source,
                "status": lead.status,
                "remarks": lead.remarks,
                "created_at": lead.created_at
            }
            for lead in leads
        ]
        return lead_list
    except Exception as e:
        raise Exception(str(e))

def log_lead_activity(lead_id, emp_id, action_type, details, old_val=None, new_val=None):
    """Utility to log lead activities."""
    try:
        log = LeadActivityLog(
            lead_id=lead_id,
            emp_id=emp_id,
            action_type=action_type,
            details=details,
            old_value=old_val,
            new_value=new_val
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error logging activity: {str(e)}")

def update_lead_service(lead_id, data, current_emp_id):
    """Updates a lead and logs status changes."""
    try:
        lead = Lead.query.get(lead_id)
        if not lead:
            return {"error": "Lead not found"}, 404

        old_status = lead.status
        new_status = data.get('status')

        # Update fields
        lead.name = data.get('name', lead.name)
        lead.lead_cat = data.get('lead_cat', lead.lead_cat)
        lead.email = data.get('email', lead.email)
        lead.mob_no = data.get('mob_no', lead.mob_no)
        lead.lead_source = data.get('lead_source', lead.lead_source)
        lead.status = new_status if new_status else lead.status
        lead.remarks = data.get('remarks', lead.remarks)
        lead.follow_up_date = data.get('follow_up_date', lead.follow_up_date)

        # Log status change if applicable
        if new_status and old_status != new_status:
            log_lead_activity(
                lead_id, 
                current_emp_id, 
                'Status Change', 
                f'Status updated from {old_status} to {new_status}', 
                old_status, 
                new_status
            )
        
        # Log other updates if needed (e.g., Note Added)
        elif data.get('remarks') and data.get('remarks') != lead.remarks:
             log_lead_activity(lead_id, current_emp_id, 'Note Added', 'Remarks updated.')

        db.session.commit()
        return {"message": "Lead updated successfully"}, 200

    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500

def add_lead_note_service(lead_id, emp_id, details):
    """Records a manual note and syncs it with the lead's main remarks."""
    try:
        # 1. Record the note in activities
        log_lead_activity(
            lead_id=lead_id,
            emp_id=emp_id,
            action_type='Note Added',
            details=details
        )

        # 2. Sync the latest remark back to the main 'leads' table
        lead = Lead.query.get(lead_id)
        if lead:
            lead.remarks = details
            db.session.commit()

        return {"message": "Note recorded and synced successfully"}, 201

    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500

def get_lead_activities_service(lead_id):
    """Fetches activity timeline for a lead."""
    try:
        activities = LeadActivityLog.query.filter_by(lead_id=lead_id).order_by(LeadActivityLog.created_at.desc()).all()
        return [
            {
                "id": act.id,
                "action_type": act.action_type,
                "details": act.details,
                "old_value": act.old_value,
                "new_value": act.new_value,
                "created_at": act.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                "emp_name": act.employee.name if act.employee else "Unknown"
            }
            for act in activities
        ], 200
    except Exception as e:
        return {"error": str(e)}, 500