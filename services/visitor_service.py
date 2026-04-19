from db import db
from models.website_visitor import WebsiteVisitor
from datetime import datetime, timedelta

class VisitorService:
    @staticmethod
    def record_visit(ip_address):
        """
        Records a new visit. To make it more meaningful, we only record 
        a 'new' visit from the same IP if it's been more than 24 hours.
        Alternatively, we can just record every visit.
        Based on user request, they want a visitors table with ip_address.
        """
        try:
            # Check if this IP has visited in the last 24 hours to avoid count bloating
            last_visit = WebsiteVisitor.query.filter_by(ip_address=ip_address)\
                        .order_by(WebsiteVisitor.visit_time.desc()).first()
            
            # If no visit or last visit was > 24 hours ago, record it as a new visit
            # For a simple 'hit counter' we could just always add, but unique visitors is better.
            # However, for 'visitor count', usually it means unique IPs.
            
            if not last_visit or (datetime.utcnow() - last_visit.visit_time) > timedelta(hours=24):
                new_visitor = WebsiteVisitor(ip_address=ip_address)
                db.session.add(new_visitor)
                db.session.commit()
            
            # Return current unique visitor count (total)
            count = db.session.query(WebsiteVisitor.ip_address).distinct().count()
            return count
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def get_total_count():
        """Returns the total unique visitor count."""
        try:
            return db.session.query(WebsiteVisitor.ip_address).distinct().count()
        except Exception as e:
            raise e
