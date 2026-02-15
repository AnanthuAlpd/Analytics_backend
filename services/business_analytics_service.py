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
    def _get_latest_year():
        """Helper to find the latest year with sales data for the demo."""
        try:
            latest_year = db.session.query(func.max(func.year(DemoSaleStats.report_date))).scalar()
            return latest_year if latest_year else datetime.now().year
        except Exception:
            return 2023  # Fallback to demo year

    @staticmethod
    def get_revenue_metrics():
        """
        Calculate comprehensive revenue and profit metrics for the latest year.
        Returns: Total revenue, total cost, gross profit, profit margin, AOV
        """
        try:
            current_year = BusinessAnalyticsService._get_latest_year()
            
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
            current_year = BusinessAnalyticsService._get_latest_year()
            
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
            # For demo purposes, we base the timeframe on the latest available data
            latest_date = db.session.query(func.max(DemoSaleStats.report_date)).scalar()
            if not latest_date:
                latest_date = datetime.now()
            
            end_date = latest_date
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
            latest_date = db.session.query(func.max(DemoSaleStats.report_date)).scalar()
            if not latest_date:
                latest_date = datetime.now()
                
            current_month_date = latest_date.replace(day=1)
            prev_month_date = (current_month_date - timedelta(days=1)).replace(day=1)
            current_year = current_month_date.year
            
            # Alert 1: Products with declining sales (>20% drop)
            declining_products = (
                db.session.query(
                    Products.product_name,
                    func.sum(case(
                        (func.month(DemoSaleStats.report_date) == current_month_date.month, 
                         DemoSaleStats.total_quantity_sold),
                        else_=0
                    )).label('current_sales'),
                    func.sum(case(
                        (func.month(DemoSaleStats.report_date) == prev_month_date.month, 
                         DemoSaleStats.total_quantity_sold),
                        else_=0
                    )).label('prev_sales')
                )
                .join(Products, DemoSaleStats.product_id == Products.product_id)
                .filter(func.year(DemoSaleStats.report_date) == current_year)
                .group_by(Products.product_name)
                .having(func.sum(case(
                    (func.month(DemoSaleStats.report_date) == prev_month_date.month, 
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
            
            current_year = BusinessAnalyticsService._get_latest_year()
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
            
            # Alert 3: Low stock for popular items (example threshold)
            low_stock_products = (
                db.session.query(
                    Products.product_name,
                    DemoSaleStats.closing_stock,
                    func.sum(DemoSaleStats.total_quantity_sold).label('total_sold')
                )
                .join(DemoSaleStats, Products.product_id == DemoSaleStats.product_id)
                .filter(func.year(DemoSaleStats.report_date) == current_year,
                        func.month(DemoSaleStats.report_date) == latest_date.month,
                        DemoSaleStats.closing_stock < 50)
                .group_by(Products.product_name, DemoSaleStats.closing_stock)
                .all()
            )

            for product in low_stock_products:
                alerts.append({
                    'type': 'warning',
                    'category': 'Inventory Management',
                    'title': f'{product.product_name} - Low Stock Alert',
                    'message': f'Only {product.closing_stock} units left at month end.',
                    'severity': 'high',
                    'action': 'Reorder immediately to prevent stock-out'
                })

            return alerts[:10]  # Return top 10 alerts
            
        except Exception as e:
            current_app.logger.error(f"Error generating business alerts: {str(e)}")
            raise

    @staticmethod
    def get_inventory_health():
        """
        Analyze inventory health: overstock, stockouts, and inventory value.
        """
        try:
            current_year = BusinessAnalyticsService._get_latest_year()
            latest_date = db.session.query(func.max(DemoSaleStats.report_date)).scalar()
            
            # 1. Total Inventory Value (at cost)
            inventory_value_query = (
                db.session.query(
                    func.sum(DemoSaleStats.closing_stock * Products.cost_price).label('total_value_cost'),
                    func.sum(DemoSaleStats.closing_stock * Products.sale_price).label('total_value_sale')
                )
                .join(Products, DemoSaleStats.product_id == Products.product_id)
                .filter(DemoSaleStats.report_date == latest_date)
                .first()
            )
            
            # 2. Identify At-Risk Products (Low stock vs Avg Monthly Sales)
            # For demo, we just look at closing stock < 20
            at_risk = (
                db.session.query(
                    Products.product_name,
                    DemoSaleStats.closing_stock
                )
                .join(DemoSaleStats, Products.product_id == DemoSaleStats.product_id)
                .filter(DemoSaleStats.report_date == latest_date,
                        DemoSaleStats.closing_stock < 20)
                .limit(5)
                .all()
            )
            
            return {
                'total_inventory_value_cost': round(float(inventory_value_query.total_value_cost or 0), 2),
                'total_inventory_value_sale': round(float(inventory_value_query.total_value_sale or 0), 2),
                'at_risk_products': [
                    {'name': row.product_name, 'stock': row.closing_stock}
                    for row in at_risk
                ],
                'status': 'Healthy' if len(at_risk) < 3 else 'Action Required'
            }
        except Exception as e:
            current_app.logger.error(f"Error fetching inventory health: {str(e)}")
            raise

    @staticmethod
    def get_top_performers(limit=5):
        """
        Get top performing products by revenue for current month.
        """
        try:
            current_year = BusinessAnalyticsService._get_latest_year()
            
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
