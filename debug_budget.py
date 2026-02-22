import sys
sys.path.append('e:/Prabhas Analytics/backend')
from app import create_app
from db import db
from models.demo_products import Products
from models.demo_sale_stats import DemoSaleStats
from sqlalchemy import func

app = create_app()

with app.app_context():
    sales_subq = db.session.query(
        DemoSaleStats.product_id,
        func.avg(DemoSaleStats.total_quantity_sold).label('avg_monthly_sales'),
        func.max(DemoSaleStats.closing_stock).label('latest_stock')
    ).group_by(DemoSaleStats.product_id).subquery()

    products_query = db.session.query(
        Products,
        sales_subq.c.avg_monthly_sales,
        sales_subq.c.latest_stock
    ).outerjoin(
        sales_subq, Products.product_id == sales_subq.c.product_id
    ).all()

    for p, avg, stock in products_query:
        print(f'Product {p.product_id} [{p.product_name}]: Cost = {p.cost_price}, Avg Sales/mo = {avg}, Current Stock = {stock}')
