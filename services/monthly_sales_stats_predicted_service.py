from models.monthly_sales_stats_predicted_model import MonthlySalesStatsPredicted

def get_predicted_monthly_totals_service():
    try:
        data = MonthlySalesStatsPredicted.get_monthly_totals()
        return {'predicted_monthly_totals': data}, 200
    except Exception as e:
        return {'error': str(e)}, 500
