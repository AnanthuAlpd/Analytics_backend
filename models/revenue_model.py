from db import db
from sqlalchemy import func
from models.demo_sale_stats import DemoSaleStats
from models.demo_predicted_sales import MonthlySalesStatsPredicted
from models.demo_products import Products

class Revenue:
    @staticmethod
    def get_revenue(table_name, qty_column, start_date, end_date):
        try:
            if table_name == 'monthly_sales_stats':
                Model = DemoSaleStats
                # qty_column should be 'total_quantity_sold', which we can map or use setattr/getattr
                # But it's safer to map strict columns if possible, but let's follow the dynamic pattern:
                qty_attr = getattr(Model, qty_column, None)
                if not qty_attr:
                     # Fallback if column name in DB is different from model attribute, but here they seem consistent
                     # For DemoSaleStats, 'total_quantity_sold' exists.
                     pass
            elif table_name == 'monthly_sales_stats_predicted':
                Model = MonthlySalesStatsPredicted
                # For MonthlySalesStatsPredicted, 'forecasted_quantity' exists.
                qty_attr = getattr(Model, qty_column, None)
            else:
                raise ValueError(f"Unknown table: {table_name}")

            if not qty_attr:
                 raise ValueError(f"Unknown column: {qty_column} in {Model.__tablename__}")

            query = db.session.query(
                func.date_format(Model.report_date, '%b').label('month'),
                func.sum(Products.sale_price * qty_attr).label('revenue')
            ).join(Products, Model.product_id == Products.product_id)\
             .filter(Model.report_date.between(start_date, end_date))\
             .group_by(Model.report_date)\
             .order_by(Model.report_date)

            results = query.all()
            return results
        except Exception as e:
            print(f"Error executing revenue query: {e}")
            raise
