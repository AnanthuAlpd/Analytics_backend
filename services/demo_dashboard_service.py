from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from flask import current_app
from sqlalchemy import func, cast, Float
from db import db
from models.demo_products import Products
from models.demo_sale_stats import DemoSaleStats
from models.demo_predicted_sales import MonthlySalesStatsPredicted
from models.demo_dashboard_card_summary import DemoDashboardCardSummary
from decimal import Decimal
from sqlalchemy import desc
from repo.sales_repo import SalesQueries

class DemoDashboardService:

    @staticmethod
    def _get_latest_year():
        """Helper to find the latest year with sales data for the demo."""
        try:
            latest_year = db.session.query(func.max(func.year(DemoSaleStats.report_date))).scalar()
            return latest_year if latest_year else datetime.now().year
        except Exception:
            return 2023  # Fallback
            
    @staticmethod
    def get_products():
        """Retrieve all products for the dashboard filter."""
        try:
            products = db.session.query(Products.product_id, Products.product_name).all()
            return [{"id": p.product_id, "name": p.product_name} for p in products]
        except Exception as e:
            current_app.logger.error(f"Error fetching products: {str(e)}")
            return []

    @staticmethod
    def get_kpi_card_data():
        try:
            current_year = DemoDashboardService._get_latest_year()
            record = DemoDashboardCardSummary.query.filter_by(year=current_year).first()
            if not record:
                return None
            # 1. Extract values safely (converting None to 0)
            total_products = record.total_products if record.total_products else 0
            predicted_sales = float(record.predicted_sales) if record.predicted_sales else 0.0
            current_growth = float(record.current_growth_rate) if record.current_growth_rate else 0.0
            predicted_growth = float(record.predicted_growth_rate) if record.predicted_growth_rate else 0.0
            accuracy = float(record.prediction_accuracy) if record.prediction_accuracy else 0.0
            monthly_avg_backorder = float(record.monthly_avg_backorder) if record.monthly_avg_backorder else 0.0
            # 2. Construct the specific dictionary you requested
            kpi_summary = {
                'totalProducts': int(total_products),
                'predictedSales': predicted_sales,
                'currentGrowthRate': current_growth,
                'predictedGrowthRate': predicted_growth,
                'monthly_avg_backorder':monthly_avg_backorder,
                'predictionAccuracy': accuracy
            }
            # 3. Round all float values to 2 decimals for clean API output
            for key, value in kpi_summary.items():
                if isinstance(value, float):
                    kpi_summary[key] = round(value, 2)
            return kpi_summary
        except Exception as e:
            current_app.logger.error(f"Error fetching KPI data: {str(e)}")
            raise Exception("Failed to fetch KPI data")
    

    @staticmethod
    def _to_series(data, series_type):
        return [
            {
                'type': series_type,
                'month': row.month,
                'total_quantity_sold': float(row.value or 0)
            }
            for row in data
        ]

    @staticmethod
    def get_monthly_comparison(product_id=None, months=None):

        actual_rows = SalesQueries.get_actual_monthly_totals(product_id, months)
        predicted_rows = SalesQueries.get_predicted_monthly_totals(product_id, months)

        actual = DemoDashboardService._to_series(actual_rows, 'actual')
        predicted = DemoDashboardService._to_series(predicted_rows, 'predicted')

        return {
            'actual': actual,
            'predicted': predicted,
            'metadata': {
                'actual_start': actual[0]['month'] if actual else None,
                'actual_end': actual[-1]['month'] if actual else None,
                'prediction_start': predicted[0]['month'] if predicted else None
            }
        }
   
    # -------------------------------
    # 1️⃣ Base Month Dictionary Helper
    # -------------------------------
    @staticmethod
    def _generate_base_month_dict(start_date: datetime, end_date: datetime):
        """
        Generates a list and dictionary for all months in the given range.
        """
        months = []
        curr = start_date.replace(day=1)
        while curr <= end_date:
            months.append(curr.strftime('%Y-%m'))
            # Move to next month
            if curr.month == 12:
                curr = curr.replace(year=curr.year + 1, month=1)
            else:
                curr = curr.replace(month=curr.month + 1)
        
        month_dict = {m: 0 for m in months}
        return months, month_dict

    # -------------------------------
    # 2️⃣ Monthly Data Fetcher
    # -------------------------------
    @staticmethod
    def _fetch_monthly_data(model, value_column, date_column, product_id=None, min_date=None, max_date=None):
        """
        Fetches the SUM of monthly sales for a given date range.
        """
        date_format = func.date_format  # ✅ MySQL-compatible
        
        # Determine actual range
        start_date = min_date if min_date else datetime(2018, 1, 1)
        end_date = max_date if max_date else datetime.now()

        # Generate base dictionary for the ENTIRE range
        months, month_dict = DemoDashboardService._generate_base_month_dict(start_date, end_date)

        # Build query
        query = db.session.query(
            date_format(date_column, '%Y-%m').label('month'),
            func.sum(value_column).label('value')
        )

        # Apply filters
        if product_id:
            query = query.filter(model.product_id == product_id)

        query = (
            query.filter(date_column >= start_date, date_column <= end_date)
                 .group_by('month')
                 .order_by('month')
        )

        # Execute and fill data
        for month, value in query.all():
            if month in month_dict:
                month_dict[month] = int(value or 0)

        # Format as ngx-charts compatible array
        series = [{"name": m, "value": month_dict[m]} for m in months]
        return series

    # -------------------------------
    # 3️⃣ Product-wise Data Aggregator
    # -------------------------------
    @staticmethod
    def get_series_for_product(product_id):
        """Get historical & predicted data for a specific product"""
        historical_series = DemoDashboardService._fetch_monthly_data(
            DemoSaleStats,
            DemoSaleStats.total_quantity_sold,
            DemoSaleStats.report_date,
            product_id
        )

        predicted_series = DemoDashboardService._fetch_monthly_data(
            MonthlySalesStatsPredicted,
            MonthlySalesStatsPredicted.forecasted_quantity,
            MonthlySalesStatsPredicted.report_date,
            product_id
        )

        return historical_series, predicted_series

    # -------------------------------
    # 4️⃣ Dashboard Data Aggregator
    # -------------------------------
    @staticmethod
    def get_sales_trend(product_id=None):
        """
        Returns formatted data for ngx-charts with NO overlap.
        Shows Historical (2018-2025) and Predicted (2026).
        """
        # 1. Define Split Point
        # Historical: 2018-01-01 to 2025-12-31
        # Predicted: 2026-01-01 to 2026-12-31
        
        actual_start = datetime(2018, 1, 1)
        actual_end = datetime(2025, 12, 31, 23, 59, 59)
        
        prediction_start = datetime(2026, 1, 1)
        prediction_end = datetime(2026, 12, 31, 23, 59, 59)

        # 2. Fetch Actual Historical Data (2018-2025)
        historical = DemoDashboardService._fetch_monthly_data(
            DemoSaleStats,
            DemoSaleStats.total_quantity_sold,
            DemoSaleStats.report_date,
            product_id,
            min_date=actual_start,
            max_date=actual_end
        )

        # 3. Fetch Predicted Data (2026)
        predicted = DemoDashboardService._fetch_monthly_data(
            MonthlySalesStatsPredicted,
            MonthlySalesStatsPredicted.forecasted_quantity,
            MonthlySalesStatsPredicted.report_date,
            product_id,
            min_date=prediction_start,
            max_date=prediction_end
        )

        return [
            {"name": "Historical Sales", "series": historical},
            {"name": "Predicted Sales", "series": predicted}
        ]
    
    @staticmethod
    def get_top_product_comparison(product_id=None, limit=10):
        """Get top products by comparing current vs predicted sales (current year)."""
        current_year = DemoDashboardService._get_latest_year()

        # ---- Historical (Current Year) ----
        historical_subq = (
            db.session.query(
                DemoSaleStats.product_id,
                func.sum(DemoSaleStats.total_quantity_sold).label("current_sales")
            )
            .filter(func.year(DemoSaleStats.report_date) == current_year)
            .group_by(DemoSaleStats.product_id)
        )
        if product_id:
            historical_subq = historical_subq.filter(DemoSaleStats.product_id == product_id)
        historical_subq = historical_subq.subquery()

        # ---- Predicted (Current Year) ----
        predicted_subq = (
            db.session.query(
                MonthlySalesStatsPredicted.product_id,
                func.sum(MonthlySalesStatsPredicted.forecasted_quantity).label("predicted_sales")
            )
            .filter(func.year(MonthlySalesStatsPredicted.report_date) == current_year)
            .group_by(MonthlySalesStatsPredicted.product_id)
        )
        if product_id:
            predicted_subq = predicted_subq.filter(MonthlySalesStatsPredicted.product_id == product_id)
        predicted_subq = predicted_subq.subquery()

        # ---- Join Both + Product Names ----
        query = (
            db.session.query(
                Products.product_name,
                func.coalesce(historical_subq.c.current_sales, 0).label("current_sales"),
                func.coalesce(predicted_subq.c.predicted_sales, 0).label("predicted_sales")
            )
            .outerjoin(historical_subq, historical_subq.c.product_id == Products.product_id)
            .outerjoin(predicted_subq, predicted_subq.c.product_id == Products.product_id)
        )

        if product_id:
            query = query.filter(Products.product_id == product_id)

        results = (
            query
            .order_by(func.coalesce(predicted_subq.c.predicted_sales, 0).desc())  # sort by predicted
            .limit(limit)
            .all()
        )

        # ---- Format for ngx-charts ----
        formatted = [
            {
                "name": r.product_name,
                "series": [
                    {"name": "Current", "value": int(r.current_sales or 0)},
                    {"name": "Predicted", "value": int(r.predicted_sales or 0)},
                ]
            }
            for r in results
        ]
        return formatted
    
    def get_total_actual_vs_predicted(product_id=None):
        """
        Returns total actual vs predicted sales for the current year.
        Optionally filters by product_id.
        Output format: ngx-charts bar chart compatible.
        """

        current_year = DemoDashboardService._get_latest_year()

        # ---- Total Actual ----
        actual_query = (
            db.session.query(
                func.sum(DemoSaleStats.total_quantity_sold)
            )
            .filter(func.year(DemoSaleStats.report_date) == current_year)
        )

        if product_id:
            actual_query = actual_query.filter(
                DemoSaleStats.product_id == product_id
            )

        total_actual = actual_query.scalar() or 0

        # ---- Total Predicted ----
        predicted_query = (
            db.session.query(
                func.sum(MonthlySalesStatsPredicted.forecasted_quantity)
            )
            .filter(func.year(MonthlySalesStatsPredicted.report_date) == current_year)
        )

        if product_id:
            predicted_query = predicted_query.filter(
                MonthlySalesStatsPredicted.product_id == product_id
            )

        total_predicted = predicted_query.scalar() or 0

        # ---- ngx-charts Bar Format ----
        return [
            {"name": "Actual", "value": int(total_actual)},
            {"name": "Predicted", "value": int(total_predicted)}
        ]


    @staticmethod
    def get_product_growth_performance(product_id=None):
        """
        Returns consolidated product growth performance (YoY) in a flat format.
        Matches the output structure of product-comparison-total.
        Metrics:
        - Current Growth: (2025 Actual vs 2024 Actual)
        - Predicted Growth: (2026 Predicted vs 2025 Actual)
        """
        current_year = DemoDashboardService._get_latest_year()
        prev_year = current_year - 1
        next_year = current_year + 1

        def get_val(model, column, year, p_id):
            query = db.session.query(func.sum(column)) \
                              .filter(func.year(model.report_date) == year)
            if p_id:
                query = query.filter(model.product_id == p_id)
            return float(query.scalar() or 0)

        # 1. Fetch sales for relevant years
        s_2024 = get_val(DemoSaleStats, DemoSaleStats.total_quantity_sold, prev_year, product_id)
        s_2025 = get_val(DemoSaleStats, DemoSaleStats.total_quantity_sold, current_year, product_id)
        s_2026_pred = get_val(MonthlySalesStatsPredicted, MonthlySalesStatsPredicted.forecasted_quantity, next_year, product_id)

        # 2. Calculation Helper
        def calc_growth(curr, prev):
            return round(((curr - prev) / prev * 100), 2) if prev > 0 else 0.0

        # 3. Format as flat list matching product-comparison-total
        return [
            {"name": "Current Growth", "value": calc_growth(s_2025, s_2024)},
            {"name": "Predicted Growth", "value": calc_growth(s_2026_pred, s_2025)}
        ]
    
    @staticmethod
    def get_forecast_summary(top_n: int = 6):
        """
        Returns forecast summary for products including:
        - current month sales
        - predicted next month
        - growth percentage
        - backlog count (static 0)
        - confidence score (prediction accuracy)
        """
        latest_date = db.session.query(func.max(DemoSaleStats.report_date)).scalar()
        if not latest_date:
            latest_date = datetime.now()
            
        today = latest_date
        current_month_start = datetime(today.year, today.month, 1)
        # Previous month
        prev_month_end = current_month_start - timedelta(days=1)
        prev_month_start = datetime(prev_month_end.year, prev_month_end.month, 1)
        # Next month
        next_month_start = datetime(today.year, today.month, 1) + timedelta(days=32)
        next_month_start = datetime(next_month_start.year, next_month_start.month, 1)

        # 1️⃣ Current month sales
        current_sales_subq = db.session.query(
            DemoSaleStats.product_id,
            func.sum(DemoSaleStats.total_quantity_sold).label('current_sales')
        ).filter(
            DemoSaleStats.report_date >= current_month_start,
            DemoSaleStats.report_date < next_month_start
        ).group_by(DemoSaleStats.product_id).subquery()

        # 2️⃣ Previous month sales
        prev_sales_subq = db.session.query(
            DemoSaleStats.product_id,
            func.sum(DemoSaleStats.total_quantity_sold).label('prev_sales')
        ).filter(
            DemoSaleStats.report_date >= prev_month_start,
            DemoSaleStats.report_date <= prev_month_end
        ).group_by(DemoSaleStats.product_id).subquery()

        # 3️⃣ Predicted next month
        predicted_subq = db.session.query(
            MonthlySalesStatsPredicted.product_id,
            func.sum(MonthlySalesStatsPredicted.forecasted_quantity).label('predicted_next_month')
        ).filter(
            func.year(MonthlySalesStatsPredicted.report_date) == next_month_start.year,
            func.month(MonthlySalesStatsPredicted.report_date) == next_month_start.month
        ).group_by(MonthlySalesStatsPredicted.product_id).subquery()

        # 4️⃣ Join with Products
        query = db.session.query(
            Products.product_id,
            Products.product_name,
            current_sales_subq.c.current_sales,
            prev_sales_subq.c.prev_sales,
            predicted_subq.c.predicted_next_month
        ).outerjoin(
            current_sales_subq, Products.product_id == current_sales_subq.c.product_id
        ).outerjoin(
            prev_sales_subq, Products.product_id == prev_sales_subq.c.product_id
        ).outerjoin(
            predicted_subq, Products.product_id == predicted_subq.c.product_id
        )

        result = []
        for row in query.all():
            # Convert Decimal to float
            current_sales = float(row.current_sales or 0)
            prev_sales = float(row.prev_sales or 0)
            predicted_next = float(row.predicted_next_month or 0)

            # Growth percentage vs previous month
            if prev_sales != 0:
                growth_percentage = (current_sales - prev_sales) / prev_sales * 100
            else:
                growth_percentage = 0

            # Confidence score (prediction accuracy)
            if current_sales != 0:
                confidence_score = ((predicted_next - current_sales) / current_sales) * 100
            else:
                confidence_score = 0

            result.append({
                "product_id": row.product_id,
                "product_name": row.product_name,
                "current_month_sales": current_sales,
                "predicted_next_month": predicted_next,
                "growth_percentage": round(growth_percentage, 2),
                "backlog_count": 0,  # Static for now
                "confidence_score": round(confidence_score, 2)
            })

        # Sort by current month sales descending and limit top N
        result = sorted(result, key=lambda x: x['current_month_sales'], reverse=True)[:top_n]

        return result