from db import mysql

class ActualSales:
    @staticmethod
    def get_monthly_totals():
        cur = mysql.connection.cursor()
        cur.execute("""
           SELECT 
            DATE_FORMAT(report_date, '%b %Y') AS month,
            SUM(total_quantity_sold) AS total_quantity_sold
            FROM monthly_sales_stats
            GROUP BY report_date
            ORDER BY DATE_FORMAT(report_date, '%Y-%m');
        """)
        results = cur.fetchall()
        cur.close()
        return results

    @staticmethod
    def to_dict(row):
        return {
            'type': 'actual',
            'month': row['month'],
            'total_quantity_sold': float(row['total_quantity_sold']) if row['total_quantity_sold'] else 0
        }