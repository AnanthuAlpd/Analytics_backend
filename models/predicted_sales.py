from db import db
from sqlalchemy import func, text
from models.demo_predicted_sales import MonthlySalesStatsPredicted
from models.demo_products import Products

class PredictedSales:
    @staticmethod
    def get_monthly_totals(product_id=None, months=None):
        try:
            query = db.session.query(
                func.date_format(MonthlySalesStatsPredicted.report_date, '%b %Y').label('month'),
                func.sum(MonthlySalesStatsPredicted.forecasted_quantity).label('forecasted_quantity_sum'),
                func.group_concat(func.distinct(MonthlySalesStatsPredicted.best_model)).label('models_used')
            )

            if product_id:
                query = query.filter(MonthlySalesStatsPredicted.product_id == product_id)

            if months:
                query = query.filter(MonthlySalesStatsPredicted.report_date >= func.date_sub(func.curdate(), text(f'INTERVAL {months} MONTH')))

            query = query.group_by(MonthlySalesStatsPredicted.report_date).order_by(func.date_format(MonthlySalesStatsPredicted.report_date, '%Y-%m'))
            
            results = query.all()
            return results
        except Exception as e:
            print(f"Error executing query: {e}")
            raise

    @staticmethod
    def get_max_forecasted_product():
        try:
            result = db.session.query(
                Products.product_name,
                MonthlySalesStatsPredicted.forecasted_quantity
            ).join(Products, MonthlySalesStatsPredicted.product_id == Products.product_id)\
             .order_by(MonthlySalesStatsPredicted.forecasted_quantity.desc())\
             .limit(1).all()
            return result
        except Exception as e:
            print(f"Error executing query: {e}")
            raise
    
    @staticmethod
    def get_max_valuable_product():
        try:
            total_forecasted_value = func.round(Products.sale_price * MonthlySalesStatsPredicted.forecasted_quantity)
            result = db.session.query(
                Products.product_name,
                Products.sale_price,
                MonthlySalesStatsPredicted.forecasted_quantity,
                total_forecasted_value.label('total_forecasted_value')
            ).join(Products, MonthlySalesStatsPredicted.product_id == Products.product_id)\
             .order_by(total_forecasted_value.desc())\
             .limit(1).all()
            return result
        except Exception as e:
            print(f"Error executing query: {e}")
            raise

    @staticmethod
    def get_total_revenue():
        try:
            result = db.session.query(
                func.round(func.sum(Products.sale_price * MonthlySalesStatsPredicted.forecasted_quantity)).label('total_forecasted_value')
            ).join(Products, MonthlySalesStatsPredicted.product_id == Products.product_id).all()
            return result
        except Exception as e:
            print(f"Error executing query: {e}")
            raise

    @staticmethod
    def to_dict(row):
        return {
            'type': 'predicted',
            'month': row.month,
            'forecasted_quantity': float(row.forecasted_quantity_sum) if row.forecasted_quantity_sum else 0,
            'models': row.models_used.split(',') if row.models_used else []
        }
