from db import mysql

class MonthlySalesStats:
    @staticmethod
    def get_monthly_totals():
        try:
            with mysql.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        DATE_FORMAT(report_date, '%b %Y') AS month_year,
                        SUM(total_quantity_sold) AS total_quantity
                    FROM monthly_sales_stats
                    GROUP BY month_year
                    ORDER BY MIN(report_date) ASC
                """)
                return cursor.fetchall()
        except Exception as e:
            raise e
