from app import create_app
from db import db
from models.demo_sale_stats import DemoSaleStats
from sqlalchemy import func

app = create_app()
with app.app_context():
    for p_id in [1, 2]:
        data = db.session.query(DemoSaleStats.report_date, DemoSaleStats.total_quantity_sold) \
                 .filter(DemoSaleStats.product_id == p_id) \
                 .limit(5).all()
        print(f"Product {p_id} data: {data}")
