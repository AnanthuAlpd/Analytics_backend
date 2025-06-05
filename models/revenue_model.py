from db import mysql
class Revenue:
    @staticmethod
    def get_revenue(table_name, qty_column, start_date, end_date):
        conn = mysql.connection
        cursor = conn.cursor()

        query = f"""
            SELECT DATE_FORMAT(s.report_date, '%%b') AS month,
            SUM(p.price * s.{qty_column}) AS revenue
            FROM {table_name} s
            JOIN product p ON p.product_id = s.product_id
            WHERE s.report_date BETWEEN %s AND %s
            GROUP BY s.report_date
            ORDER BY s.report_date
            """
        cursor.execute(query, (start_date, end_date))
        data = cursor.fetchall()
        return data
