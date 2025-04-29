from flask_mysqldb import MySQLdb
from db import mysql

class SalesChart:
    @staticmethod
    def get_sales_data():
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            # Step 1: Get the latest actual sales month
            cursor.execute("""
                SELECT MAX(DATE_FORMAT(report_date, '%%Y-%%m-01')) AS latest_actual_month
                FROM monthly_sales_stats
            """)
            result = cursor.fetchone()

            if not result or not result['latest_actual_month']:
                print("No actual sales data found.")
                return []

            latest_actual_month = result['latest_actual_month']
            print(f"[DEBUG] Latest Actual Sales Month: {latest_actual_month}")

            # Step 2: Fetch actual sales data (up to latest_actual_month)
            cursor.execute("""
                SELECT 
                    DATE_FORMAT(report_date, '%%b %%Y') AS month,
                    total_quantity_sold AS value
                FROM monthly_sales_stats
                WHERE DATE_FORMAT(report_date, '%%Y-%%m-01') <= %s
                ORDER BY report_date
            """, (latest_actual_month,))
            actual_sales = cursor.fetchall()

            print(f"[DEBUG] Actual Sales Fetched: {actual_sales}")

            # Step 3: Fetch predicted sales data (after latest_actual_month)
            cursor.execute("""
                SELECT 
                    DATE_FORMAT(report_date, '%%b %%Y') AS month,
                    forecasted_quantity AS value
                FROM monthly_sales_stats_predicted
                WHERE DATE_FORMAT(report_date, '%%Y-%%m-01') > %s
                ORDER BY report_date
            """, (latest_actual_month,))
            predicted_sales = cursor.fetchall()

            print(f"[DEBUG] Predicted Sales Fetched: {predicted_sales}")

            # Step 4: Prepare data for ngx-line-chart
            chart_data = [
                {
                    "name": "Actual Sales",
                    "series": actual_sales
                },
                {
                    "name": "Predicted Sales",
                    "series": predicted_sales
                }
            ]

            print(f"[DEBUG] Final Chart Data: {chart_data}")

            return chart_data

        except Exception as e:
            print(f"[ERROR] Exception in get_sales_data: {str(e)}")
            return []
