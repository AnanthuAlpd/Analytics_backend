from datetime import datetime, timedelta
from sqlalchemy import func, extract
from db import db
from models.leads import Lead

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