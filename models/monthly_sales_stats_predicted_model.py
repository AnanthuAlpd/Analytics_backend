from db import mysql

class MonthlySalesStatsPredicted:
    @staticmethod
    def get_monthly_totals():
        query = """
            SELECT 
                DATE_FORMAT(report_date, '%b %Y') AS month_year,
                SUM(forecasted_quantity) AS total_forecasted_quantity
            FROM monthly_sales_stats_predicted
            GROUP BY month_year
            ORDER BY MIN(report_date) ASC;
        """
        try:
            cursor = mysql.connection.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            return results
        except Exception as e:
            print(f"Error: {str(e)}")
            return None

