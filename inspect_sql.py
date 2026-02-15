from app import create_app
from db import db
from models.demo_sale_stats import DemoSaleStats
from sqlalchemy import func

app = create_app()
with app.app_context():
    for p_id in [1, 2, 5, 10]:
        query = db.session.query(func.sum(DemoSaleStats.total_quantity_sold)) \
                          .filter(func.year(DemoSaleStats.report_date) == 2025) \
                          .filter(DemoSaleStats.product_id == p_id)
        
        # Print the SQL
        print(f"SQL for ID {p_id}: {query}")
        
        val = query.scalar()
        print(f"Product {p_id} 2025 sales: {val}")

    # Check the count of records per product
    counts = db.session.query(DemoSaleStats.product_id, func.count('*')) \
                       .group_by(DemoSaleStats.product_id).limit(5).all()
    print(f"Record counts per product: {counts}")
