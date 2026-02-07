from flask import current_app
from sqlalchemy import func, case, and_, or_
from db import db
from models.demo_products import Products
from models.demo_sale_stats import DemoSaleStats
from models.demo_predicted_sales import MonthlySalesStatsPredicted
from datetime import datetime, timedelta
from decimal import Decimal

class BusinessAnalyticsService:
    """
    Enhanced analytics service for client-facing business intelligence.
    Provides revenue metrics, inventory health, alerts, and recommendations.
    """

    @staticmethod
    def get_revenue_metrics():
        """
        Calculate comprehensive revenue and profit metrics for the current year.
        Returns: Total revenue, total cost, gross profit, profit margin, AOV
        """
        try:
            # Use 2023 as current year for demo (where data exists)
            current_year = 2023
            
            # Get sales data with product pricing
            revenue_query = (
                db.session.query(
                    func.sum(DemoSaleStats.total_quantity_sold * Products.sale_price).label('total_revenue'),
                    func.sum(DemoSaleStats.total_quantity_sold * Products.cost_price).label('total_cost'),
                    func.count(DemoSaleStats.stats_id).label('transaction_count'),
                    func.sum(DemoSaleStats.total_quantity_sold).label('total_units')
                )
                .join(Products, DemoSaleStats.product_id == Products.product_id)
                .filter(func.year(DemoSaleStats.report_date) == current_year)
                .first()
            )
            
            total_revenue = float(revenue_query.total_revenue or 0)
            total_cost = float(revenue_query.total_cost or 0)
            transaction_count = int(revenue_query.transaction_count or 1)
            total_units = int(revenue_query.total_units or 0)
            
            gross_profit = total_revenue - total_cost
            profit_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0
            # Calculate AOV as revenue per sales record
            avg_order_value = total_revenue / transaction_count if transaction_count > 0 else 0
            
            # Get previous year for comparison
            prev_year = current_year - 1
            prev_revenue_query = (
                db.session.query(
                    func.sum(DemoSaleStats.total_quantity_sold * Products.sale_price).label('prev_revenue')
                )
                .join(Products, DemoSaleStats.product_id == Products.product_id)
                .filter(func.year(DemoSaleStats.report_date) == prev_year)
                .first()
            )
            
            prev_revenue = float(prev_revenue_query.prev_revenue or 0)
            revenue_growth = ((total_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0
            
            return {
                'total_revenue': round(total_revenue, 2),
                'total_cost': round(total_cost, 2),
                'gross_profit': round(gross_profit, 2),
                'profit_margin': round(profit_margin, 2),
                'avg_order_value': round(avg_order_value, 2),
                'total_units_sold': total_units,
                'revenue_growth_yoy': round(revenue_growth, 2)
            }
            
        except Exception as e:
            current_app.logger.error(f"Error calculating revenue metrics: {str(e)}")
            raise

    @staticmethod
    def get_category_performance():
        """
        Get sales performance breakdown by product category.
        Returns data formatted for pie/donut chart.
        """
        try:
            # Use 2023 as current year for demo (where data exists)
            current_year = 2023
            
            category_data = (
                db.session.query(
                    Products.category,
                    func.sum(DemoSaleStats.total_quantity_sold).label('total_units'),
                    func.sum(DemoSaleStats.total_quantity_sold * Products.sale_price).label('revenue')
                )
                .join(Products, DemoSaleStats.product_id == Products.product_id)
                .filter(func.year(DemoSaleStats.report_date) == current_year)
                .group_by(Products.category)
                .order_by(func.sum(DemoSaleStats.total_quantity_sold * Products.sale_price).desc())
                .all()
            )
            
            # Format for ngx-charts
            result = [
                {
                    'name': row.category,
                    'value': int(row.total_units or 0),
                    'extra': {
                        'revenue': round(float(row.revenue or 0), 2)
                    }
                }
                for row in category_data
            ]
            
            return result
            
        except Exception as e:
            current_app.logger.error(f"Error fetching category performance: {str(e)}")
            raise

    @staticmethod
    def get_revenue_trend(months=12):
        """
        Get monthly revenue and profit trend for the specified number of months.
        Returns data for line chart showing revenue vs cost over time.
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=months * 30)
            
            monthly_data = (
                db.session.query(
                    func.date_format(DemoSaleStats.report_date, '%Y-%m').label('month'),
                    func.sum(DemoSaleStats.total_quantity_sold * Products.sale_price).label('revenue'),
                    func.sum(DemoSaleStats.total_quantity_sold * Products.cost_price).label('cost')
                )
                .join(Products, DemoSaleStats.product_id == Products.product_id)
                .filter(DemoSaleStats.report_date >= start_date)
                .group_by('month')
                .order_by('month')
                .all()
            )
            
            # Format for ngx-charts multi-series
            revenue_series = []
            profit_series = []
            
            for row in monthly_data:
                revenue = float(row.revenue or 0)
                cost = float(row.cost or 0)
                profit = revenue - cost
                
                revenue_series.append({'name': row.month, 'value': round(revenue, 2)})
                profit_series.append({'name': row.month, 'value': round(profit, 2)})
            
            return [
                {'name': 'Revenue', 'series': revenue_series},
                {'name': 'Gross Profit', 'series': profit_series}
            ]
            
        except Exception as e:
            current_app.logger.error(f"Error fetching revenue trend: {str(e)}")
            raise

    @staticmethod
    def get_business_alerts():
        """
        Generate business alerts for issues requiring attention.
        Returns list of alerts with severity and actionable insights.
        """
        try:
            alerts = []
            current_month = datetime.now().replace(day=1)
            prev_month = (current_month - timedelta(days=1)).replace(day=1)
            
            # Alert 1: Products with declining sales (>20% drop)
            declining_products = (
                db.session.query(
                    Products.product_name,
                    func.sum(case(
                        (func.month(DemoSaleStats.report_date) == current_month.month, 
                         DemoSaleStats.total_quantity_sold),
                        else_=0
                    )).label('current_sales'),
                    func.sum(case(
                        (func.month(DemoSaleStats.report_date) == prev_month.month, 
                         DemoSaleStats.total_quantity_sold),
                        else_=0
                    )).label('prev_sales')
                )
                .join(Products, DemoSaleStats.product_id == Products.product_id)
                .filter(func.year(DemoSaleStats.report_date) == 2023)
                .group_by(Products.product_name)
                .having(func.sum(case(
                    (func.month(DemoSaleStats.report_date) == prev_month.month, 
                     DemoSaleStats.total_quantity_sold),
                    else_=0
                )) > 0)
                .all()
            )
            
            for product in declining_products:
                current = float(product.current_sales or 0)
                previous = float(product.prev_sales or 0)
                
                if previous > 0:
                    decline_pct = ((current - previous) / previous) * 100
                    if decline_pct < -20:
                        alerts.append({
                            'type': 'warning',
                            'category': 'Sales Performance',
                            'title': f'{product.product_name} - Declining Sales',
                            'message': f'Sales dropped {abs(decline_pct):.1f}% this month',
                            'severity': 'high' if decline_pct < -40 else 'medium',
                            'action': 'Review pricing or marketing strategy'
                        })
            
            # Alert 2: Products exceeding forecast (positive surprise)
            current_year = 2023
            outperforming = (
                db.session.query(
                    Products.product_name,
                    func.sum(DemoSaleStats.total_quantity_sold).label('actual'),
                    func.sum(MonthlySalesStatsPredicted.forecasted_quantity).label('predicted')
                )
                .join(Products, DemoSaleStats.product_id == Products.product_id)
                .outerjoin(MonthlySalesStatsPredicted, 
                          and_(DemoSaleStats.product_id == MonthlySalesStatsPredicted.product_id,
                               func.year(DemoSaleStats.report_date) == func.year(MonthlySalesStatsPredicted.report_date)))
                .filter(func.year(DemoSaleStats.report_date) == current_year)
                .group_by(Products.product_name)
                .all()
            )
            
            for product in outperforming:
                actual = float(product.actual or 0)
                predicted = float(product.predicted or 0)
                
                if predicted > 0 and actual > predicted * 1.2:  # 20% above forecast
                    exceed_pct = ((actual - predicted) / predicted) * 100
                    alerts.append({
                        'type': 'success',
                        'category': 'Sales Performance',
                        'title': f'{product.product_name} - Exceeding Forecast',
                        'message': f'Sales {exceed_pct:.1f}% above prediction',
                        'severity': 'info',
                        'action': 'Consider increasing inventory'
                    })
            
            return alerts[:10]  # Return top 10 alerts
            
        except Exception as e:
            current_app.logger.error(f"Error generating business alerts: {str(e)}")
            raise

    @staticmethod
    def get_top_performers(limit=5):
        """
        Get top performing products by revenue for current month.
        """
        try:
            # Use 2023 data for demo
            current_year = 2023
            
            top_products = (
                db.session.query(
                    Products.product_name,
                    func.sum(DemoSaleStats.total_quantity_sold).label('units_sold'),
                    func.sum(DemoSaleStats.total_quantity_sold * Products.sale_price).label('revenue')
                )
                .join(Products, DemoSaleStats.product_id == Products.product_id)
                .filter(func.year(DemoSaleStats.report_date) == current_year)
                .group_by(Products.product_name)
                .order_by(func.sum(DemoSaleStats.total_quantity_sold * Products.sale_price).desc())
                .limit(limit)
                .all()
            )
            
            return [
                {
                    'product_name': row.product_name,
                    'units_sold': int(row.units_sold or 0),
                    'revenue': round(float(row.revenue or 0), 2)
                }
                for row in top_products
            ]
            
        except Exception as e:
            current_app.logger.error(f"Error fetching top performers: {str(e)}")
            raise
