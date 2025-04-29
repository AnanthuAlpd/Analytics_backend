from db import mysql

class PredictedSales:
    @staticmethod
    def get_monthly_totals():
        cur = mysql.connection.cursor()
        cur.execute("""
             SELECT 
                DATE_FORMAT(report_date, '%b %Y') AS month,
                SUM(forecasted_quantity) AS forecasted_quantity_sum,
                GROUP_CONCAT(DISTINCT best_model) AS models_used
                FROM monthly_sales_stats_predicted
                GROUP BY report_date, month
                ORDER BY report_date;
        """)
        results = cur.fetchall()
        cur.close()
        return results

    @staticmethod
    def to_dict(row):
        return {
            'type': 'predicted',
            'month': row['month'],
            'forecasted_quantity': float(row['forecasted_quantity_sum']) if row['forecasted_quantity_sum'] else 0,
            'models': row['models_used'].split(',') if row['models_used'] else []
        }