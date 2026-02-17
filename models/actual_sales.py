from db import db
from sqlalchemy import func, text
from models.demo_sale_stats import DemoSaleStats
from models.demo_products import Products
from models.demo_predicted_sales import MonthlySalesStatsPredicted

class ActualSales:
    @staticmethod
    def get_monthly_totals(product_id=None, months=None):
        try:
            query = db.session.query(
                func.date_format(DemoSaleStats.report_date, '%b %Y').label('month'),
                func.sum(DemoSaleStats.total_quantity_sold).label('total_quantity_sold')
            )

            if product_id:
                query = query.filter(DemoSaleStats.product_id == product_id)

            if months:
                # Using text for interval since SQLAlchemy doesn't support it directly in func widely for all dialects easily without text
                query = query.filter(DemoSaleStats.report_date >= func.date_sub(func.curdate(), text(f'INTERVAL {months} MONTH')))

            query = query.group_by(DemoSaleStats.report_date).order_by(func.date_format(DemoSaleStats.report_date, '%Y-%m'))
            
            results = query.all()
            return results
        except Exception as e:
            print(f"Error executing query: {e}")
            raise

    @staticmethod
    def to_dict(row):
        return {
            'type': 'actual',
            'month': row.month,
            'total_quantity_sold': float(row.total_quantity_sold) if row.total_quantity_sold else 0
        }

    @staticmethod
    def get_comparison_table():
        try:
            # Subquery for Actual Sales 2022
            sq_actual = db.session.query(
                DemoSaleStats.product_id,
                func.sum(DemoSaleStats.total_quantity_sold).label('actual_sale_2022')
            ).filter(func.year(DemoSaleStats.report_date) == 2022)\
             .group_by(DemoSaleStats.product_id).subquery()

            # Subquery for Predicted Sales 2023
            sq_predicted = db.session.query(
                MonthlySalesStatsPredicted.product_id,
                func.sum(MonthlySalesStatsPredicted.forecasted_quantity).label('predicted_sale_2023')
            ).group_by(MonthlySalesStatsPredicted.product_id).subquery()

            # Main Query
            results = db.session.query(
                Products.product_name,
                Products.product_id,
                func.coalesce(sq_actual.c.actual_sale_2022, 0).label('actual_sale_2022'),
                func.coalesce(sq_predicted.c.predicted_sale_2023, 0).label('predicted_sale_2023')
            ).outerjoin(sq_actual, Products.product_id == sq_actual.c.product_id)\
             .outerjoin(sq_predicted, Products.product_id == sq_predicted.c.product_id)\
             .filter(Products.product_id.notin_([51, 52, 53]))\
             .order_by(Products.product_id).all()

            return [
                {
                    "product_id": row.product_id,
                    "product_name": row.product_name,
                    "actual_sale_2022": float(row.actual_sale_2022 or 0),
                    "predicted_sale_2023": round(float(row.predicted_sale_2023 or 0), 2)
                }
                for row in results
            ]

        except Exception as e:
            print(f"Error fetching comparison table: {e}")
            raise
