from models.revenue_model import Revenue

def get_monthly_revenue_comparison():
    actual = Revenue.get_revenue("monthly_sales_stats", "total_quantity_sold", "2022-01-01", "2022-06-01")
    predicted = Revenue.get_revenue("monthly_sales_stats_predicted", "forecasted_quantity", "2023-01-01", "2023-06-01")

    return [
        {"name": "Actual Sale 2022", "series": [{"name": r["month"], "value": float(r["revenue"])} for r in actual]},
        {"name": "Predicted Sale 2023", "series": [{"name": r["month"], "value": float(r["revenue"])} for r in predicted]},
    ]
