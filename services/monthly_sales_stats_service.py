from models.monthly_sales_stats_model import MonthlySalesStats

def get_monthly_totals_service():
    try:
        data = MonthlySalesStats.get_monthly_totals()
        return {'monthly_totals': data}, 200
    except Exception as e:
        return {'error': str(e)}, 500
