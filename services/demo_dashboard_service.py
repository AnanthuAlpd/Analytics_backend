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
    def get_kpi_card_data():
        try:
            current_year = datetime.now().year
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
    def _generate_base_month_dict(year: int):
        """
        Generates a list and dictionary for all 12 months of the given year.
        Example:
            months = ['2025-01', '2025-02', ..., '2025-12']
            month_dict = {'2025-01': 0, ..., '2025-12': 0}
        """
        months = [f"{year}-{str(m).zfill(2)}" for m in range(1, 13)]
        month_dict = {m: 0 for m in months}
        return months, month_dict

    # -------------------------------
    # 2️⃣ Monthly Data Fetcher
    # -------------------------------
    @staticmethod
    def _fetch_monthly_data(model, value_column, date_column, product_id=None):
        """
        Fetches the SUM of monthly sales (historical or predicted) for a given year.
        Supports both:
          - Single product mode (when product_id is given)
          - All-products combined mode (when product_id is None)
        """
        date_format = func.date_format  # ✅ MySQL-compatible
        current_year = datetime.now().year
        start_date = datetime(current_year, 1, 1)
        end_date = datetime(current_year, 12, 31, 23, 59, 59)

        # Generate base dictionary
        months, month_dict = DemoDashboardService._generate_base_month_dict(current_year)

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

        # Debug SQL (optional)
        # print(str(query.statement.compile(compile_kwargs={"literal_binds": True})))

        # Execute and fill data
        for month, value in query.all():
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
        Returns formatted data for ngx-charts.
        If product_id is provided → individual product data.
        Else → total sales across all products.
        """
        if product_id:
            # Single product mode
            historical, predicted = DemoDashboardService.get_series_for_product(product_id)
        else:
            # All products combined mode (sum of all)
            historical = DemoDashboardService._fetch_monthly_data(
                DemoSaleStats,
                DemoSaleStats.total_quantity_sold,
                DemoSaleStats.report_date
            )
            predicted = DemoDashboardService._fetch_monthly_data(
                MonthlySalesStatsPredicted,
                MonthlySalesStatsPredicted.forecasted_quantity,
                MonthlySalesStatsPredicted.report_date
            )

        return [
            {"name": "Historical Sales", "series": historical},
            {"name": "Predicted Sales", "series": predicted}
        ]
    
    @staticmethod
    def get_top_product_comparison(limit=10):
        """Get top products by comparing current vs predicted sales (current year)."""
        current_year = datetime.now().year

        # ---- Historical (Current Year) ----
        historical_subq = (
            db.session.query(
                DemoSaleStats.product_id,
                func.sum(DemoSaleStats.total_quantity_sold).label("current_sales")
            )
            .filter(func.year(DemoSaleStats.report_date) == current_year)
            .group_by(DemoSaleStats.product_id)
            .subquery()
        )

        # ---- Predicted (Current Year) ----
        predicted_subq = (
            db.session.query(
                MonthlySalesStatsPredicted.product_id,
                func.sum(MonthlySalesStatsPredicted.forecasted_quantity).label("predicted_sales")
            )
            .filter(func.year(MonthlySalesStatsPredicted.report_date) == current_year)
            .group_by(MonthlySalesStatsPredicted.product_id)
            .subquery()
        )

        # ---- Join Both + Product Names ----
        results = (
            db.session.query(
                Products.product_name,
                func.coalesce(historical_subq.c.current_sales, 0).label("current_sales"),
                func.coalesce(predicted_subq.c.predicted_sales, 0).label("predicted_sales")
            )
            .outerjoin(historical_subq, historical_subq.c.product_id == Products.product_id)
            .outerjoin(predicted_subq, predicted_subq.c.product_id == Products.product_id)
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
        #print(formatted)
        return formatted
    
    def get_total_actual_vs_predicted(product_id=None):
        """
        Returns total actual vs predicted sales for the current year.
        Optionally filters by product_id.
        Output format: ngx-charts bar chart compatible.
        """

        current_year = datetime.now().year

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
    def get_product_growth_performance(top_n: int = 6):
        """
        Returns product growth performance in ngx-charts grouped-series format:
        [
            {
                "name": "Smartphone X1",
                "series": [
                    { "name": "Historical Growth", "value": 20.5 },
                    { "name": "Predicted Growth", "value": 15.8 }
                ]
            },
            ...
        ]
        """
        current_year = datetime.now().year
        previous_year = current_year - 1

        # 1️⃣ Sum historical sales for current and previous year
        historical_current = db.session.query(
            DemoSaleStats.product_id,
            func.sum(DemoSaleStats.total_quantity_sold).label('current_sales')
        ).filter(func.year(DemoSaleStats.report_date) == current_year
        ).group_by(DemoSaleStats.product_id).subquery()

        historical_previous = db.session.query(
            DemoSaleStats.product_id,
            func.sum(DemoSaleStats.total_quantity_sold).label('previous_sales')
        ).filter(func.year(DemoSaleStats.report_date) == previous_year
        ).group_by(DemoSaleStats.product_id).subquery()

        # 2️⃣ Sum predicted sales for current year
        predicted_sales = db.session.query(
            MonthlySalesStatsPredicted.product_id,
            func.sum(MonthlySalesStatsPredicted.forecasted_quantity).label('predicted_sales')
        ).filter(func.year(MonthlySalesStatsPredicted.report_date) == current_year
        ).group_by(MonthlySalesStatsPredicted.product_id).subquery()

        # 3️⃣ Join with product table
        query = db.session.query(
            Products.product_name,
            historical_current.c.current_sales,
            historical_previous.c.previous_sales,
            predicted_sales.c.predicted_sales
        ).outerjoin(
            historical_current, Products.product_id == historical_current.c.product_id
        ).outerjoin(
            historical_previous, Products.product_id == historical_previous.c.product_id
        ).outerjoin(
            predicted_sales, Products.product_id == predicted_sales.c.product_id
        )

        result = []
        for row in query.all():
            # Convert Decimal to float
            current_sales = float(row.current_sales or 0)
            previous_sales = float(row.previous_sales or 0)
            predicted_sales_value = float(row.predicted_sales or 0)

            # Historical YoY Growth %
            if previous_sales != 0:
                historical_growth = (current_sales - previous_sales) / previous_sales * 100
            else:
                historical_growth = 0

            # Predicted Growth %
            if current_sales != 0:
                predicted_growth = (predicted_sales_value - current_sales) / current_sales * 100
            else:
                predicted_growth = 0

            # Map to ngx-charts grouped-series format
            result.append({
                "name": row.product_name,
                "series": [
                    { "name": "Historical Growth", "value": round(historical_growth, 2) },
                    { "name": "Predicted Growth", "value": round(predicted_growth, 2) }
                ]
            })

        # Sort by historical growth descending and limit top N
        result = sorted(result, key=lambda x: x['series'][0]['value'], reverse=True)[:top_n]

        return result
    
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
        today = datetime.now()
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