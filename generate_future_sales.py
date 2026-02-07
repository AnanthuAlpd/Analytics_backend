from app import create_app
from db import mysql


app = create_app()

def sync_sales_table():
    with app.app_context():
        cur = mysql.connection.cursor()

        # Create or replace tmp_stock table
        cur.execute("""
            CREATE TEMPORARY TABLE IF NOT EXISTS tmp_stock (
                stats_id INT,
                product_id INT,
                report_date DATE,
                opening_stock INT,
                closing_stock INT,
                PRIMARY KEY (stats_id)
            )
        """)

        # Get all products
        cur.execute("SELECT DISTINCT product_id FROM monthly_sales_stats ORDER BY product_id")
        products = [row[0] for row in cur.fetchall()]

        for product_id in products:
            # Get monthly_sales_stats for the product, ordered by report_date
            cur.execute("""
                SELECT stats_id, report_date, COALESCE(stock_purchased, 0), COALESCE(total_quantity_sold, 0)
                FROM monthly_sales_stats
                WHERE product_id = %s
                ORDER BY report_date
            """, (product_id,))
            sales_data = cur.fetchall()

            # Get bi_annual_stock_taking for the product
            cur.execute("""
                SELECT stock_date, stock_purchased
                FROM bi_annual_stock_taking
                WHERE product_id = %s
                ORDER BY stock_date
            """, (product_id,))
            stock_taking_data = {row[0]: row[1] for row in cur.fetchall()}

            prev_closing_stock = 0
            for i, (stats_id, report_date, stock_purchased, total_quantity_sold) in enumerate(sales_data):
                year = report_date.year
                month = report_date.month
                is_stock_taking = (month in (1, 6) and report_date in stock_taking_data)

                # Calculate opening_stock
                if year == 2018 and month == 1:
                    opening_stock = 0
                elif is_stock_taking:
                    opening_stock = prev_closing_stock + stock_taking_data.get(report_date, 0)
                else:
                    opening_stock = prev_closing_stock

                # Calculate closing_stock
                if is_stock_taking:
                    closing_stock = opening_stock - total_quantity_sold
                else:
                    closing_stock = opening_stock + stock_purchased - total_quantity_sold

                # Insert into tmp_stock
                cur.execute("""
                    INSERT INTO tmp_stock (stats_id, product_id, report_date, opening_stock, closing_stock)
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        opening_stock = VALUES(opening_stock),
                        closing_stock = VALUES(closing_stock)
                """, (stats_id, product_id, report_date, opening_stock, closing_stock))

                prev_closing_stock = closing_stock

        mysql.connection.commit()
        cur.close()

if __name__ == '__main__':
    sync_sales_table()