# from db import db

# class MonthlySales(db.Model):
#     __tablename__ = 'mas_monthly_sales_stats'

#     stats_id = db.Column(db.Integer, primary_key=True)
#     report_date = db.Column(db.Date, nullable=False)
#     product_id = db.Column(db.Integer, db.ForeignKey('pr_product_master.product_id'), nullable=False)
#     client = db.Column(db.Integer)
#     qty_sold = db.Column(db.Integer, nullable=False)
#     client_id = db.Column(db.Integer, nullable=False)
#     created_at = db.Column(db.DateTime)
#     updated_at = db.Column(db.DateTime)
