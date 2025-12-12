from db import mysql

class PredictedSales:
    @staticmethod
    def get_monthly_totals(product_id=None, months=None):
        cur = mysql.connection.cursor()

        query = """
            SELECT 
                DATE_FORMAT(report_date, '%%b %%Y') AS month,
                SUM(forecasted_quantity) AS forecasted_quantity_sum,
                GROUP_CONCAT(DISTINCT best_model) AS models_used
            FROM monthly_sales_stats_predicted
            WHERE 1=1
        """
        params = []

        if product_id:
            query += " AND product_id = %s"
            params.append(product_id)

        if months:
            query += " AND report_date >= DATE_SUB(CURDATE(), INTERVAL %s MONTH)"
            params.append(months)

        query += " GROUP BY report_date ORDER BY DATE_FORMAT(report_date, '%%Y-%%m')"

        #print(f"Executing query:\n{query} with parameters: {params}")

        try:
            cur.execute(query, tuple(params))
            results = cur.fetchall()
            cur.close()
            return results
        except Exception as e:
            print(f"Error executing query: {e}")
            raise

    @staticmethod
    def get_max_forecasted_product():
        conn = mysql.connection
        cursor = conn.cursor()

        query = f"""
            SELECT 
            b.product_name,
            a.forecasted_quantity
            FROM 
            monthly_sales_stats_predicted a
            JOIN 
            product b ON a.product_id = b.product_id
            ORDER BY 
            a.forecasted_quantity DESC
            LIMIT 1
            """
        cursor.execute(query)
        data = cursor.fetchall()
        return data
    
    @staticmethod
    def get_max_valuable_product():
        conn = mysql.connection
        cursor = conn.cursor()

        query = f"""
            SELECT 
            b.product_name,
            b.sale_price,
            a.forecasted_quantity,
            round(b.sale_price * a.forecasted_quantity) AS total_forecasted_value
            FROM 
            monthly_sales_stats_predicted a
            JOIN 
            product b ON a.product_id = b.product_id
            ORDER BY 
            total_forecasted_value DESC
            LIMIT 1
            """
        cursor.execute(query)
        data = cursor.fetchall()
        return data
    @staticmethod
    def get_total_revenue():
        conn = mysql.connection
        cursor = conn.cursor()

        query = f"""
            SELECT 
            ROUND(SUM(b.sale_price * a.forecasted_quantity)) AS total_forecasted_value
            FROM 
            monthly_sales_stats_predicted a
            JOIN 
            product b ON a.product_id = b.product_id
            """
        cursor.execute(query)
        data = cursor.fetchall()
        return data

    @staticmethod
    def to_dict(row):
        return {
            'type': 'predicted',
            'month': row['month'],
            'forecasted_quantity': float(row['forecasted_quantity_sum']) if row['forecasted_quantity_sum'] else 0,
            'models': row['models_used'].split(',') if row['models_used'] else []
        }
