from db import mysql

class ActualSales:
    @staticmethod
    def get_monthly_totals(product_id=None, months=None):
        cur = mysql.connection.cursor()

        query = """
            SELECT 
                DATE_FORMAT(report_date, '%%b %%Y') AS month,
                SUM(total_quantity_sold) AS total_quantity_sold
            FROM monthly_sales_stats
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

        print(f"Executing query:\n{query} with parameters: {params}")

        try:
            cur.execute(query, tuple(params))
            results = cur.fetchall()
            cur.close()
            return results
        except Exception as e:
            print(f"Error executing query: {e}")
            raise

    @staticmethod
    def to_dict(row):
        return {
            'type': 'actual',
            'month': row['month'],
            'total_quantity_sold': float(row['total_quantity_sold']) if row['total_quantity_sold'] else 0
        }
    @staticmethod
    def get_comparison_table():
        cur = mysql.connection.cursor()

        query = """
                SELECT 
    p.product_name,
    p.product_id,
    COALESCE(a.actual_sale_2022, 0) AS actual_sale_2022,
    COALESCE(pf.predicted_sale_2023, 0) AS predicted_sale_2023
FROM product p
LEFT JOIN (
    SELECT 
        product_id,
        SUM(total_quantity_sold) AS actual_sale_2022
    FROM monthly_sales_stats
    WHERE YEAR(report_date) = 2022
    GROUP BY product_id
) a ON p.product_id = a.product_id
LEFT JOIN (
    SELECT 
        product_id,
        SUM(forecasted_quantity) AS predicted_sale_2023
    FROM monthly_sales_stats_predicted
    GROUP BY product_id
) pf ON p.product_id = pf.product_id
WHERE p.product_id NOT IN (51, 52, 53)
ORDER BY p.product_id
        """

        try:
            cur.execute(query)
            results = cur.fetchall()
            cur.close()
            return [
                {
                    "product_id": row["product_id"],
                    "product_name": row["product_name"],
                    "actual_sale_2022": float(row["actual_sale_2022"] or 0),
                    "predicted_sale_2023": round(float(row["predicted_sale_2023"] or 0), 2)
                }
                for row in results
            ]
        except Exception as e:
            print(f"Error fetching comparison table: {e}")
            raise
