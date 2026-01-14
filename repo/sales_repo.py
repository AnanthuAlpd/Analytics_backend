from sqlalchemy import func
from db import db
#from models.monthly_sales_stats import MonthlySalesStats
from models.demo_predicted_sales import MonthlySalesStatsPredicted
from models.demo_sale_stats import DemoSaleStats


class SalesQueries:

    @staticmethod
    def get_actual_monthly_totals(product_id=None, months=None):
        month_expr = func.date_format(DemoSaleStats.report_date, '%Y-%m')

        query = (
            db.session.query(
                month_expr.label('month_key'),
                func.date_format(
                    func.min(DemoSaleStats.report_date), '%b %Y'
                ).label('month'),
                func.sum(DemoSaleStats.total_quantity_sold).label('value')
            )
        )

        if product_id:
            query = query.filter(
                DemoSaleStats.product_id == product_id
            )

        if months:
            query = query.filter(
                DemoSaleStats.report_date >=
                func.date_sub(func.curdate(), func.interval(months, 'MONTH'))
            )

        return (
            query
            .group_by(month_expr)
            .order_by(month_expr)
            .all()
        )

    @staticmethod
    def get_predicted_monthly_totals(product_id=None, months=None):
        month_expr = func.date_format(
            MonthlySalesStatsPredicted.report_date, '%Y-%m'
        )

        query = (
            db.session.query(
                month_expr.label('month_key'),
                func.date_format(
                    func.min(MonthlySalesStatsPredicted.report_date), '%b %Y'
                ).label('month'),
                func.sum(
                    MonthlySalesStatsPredicted.forecasted_quantity
                ).label('value')
            )
        )

        if product_id:
            query = query.filter(
                MonthlySalesStatsPredicted.product_id == product_id
            )

        if months:
            query = query.filter(
                MonthlySalesStatsPredicted.report_date >=
                func.date_sub(func.curdate(), func.interval(months, 'MONTH'))
            )

        return (
            query
            .group_by(month_expr)
            .order_by(month_expr)
            .all()
        )
