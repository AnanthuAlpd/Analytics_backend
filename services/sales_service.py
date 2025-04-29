from models.actual_sales import ActualSales
from models.predicted_sales import PredictedSales

class SalesService:
    @staticmethod
    def get_monthly_comparison():
        actual = [ActualSales.to_dict(row) for row in ActualSales.get_monthly_totals()]
        predicted = [PredictedSales.to_dict(row) for row in PredictedSales.get_monthly_totals()]
        
        return {
            'actual': actual,
            'predicted': predicted,
            'metadata': {
                'actual_start': actual[0]['month'] if actual else None,
                'actual_end': actual[-1]['month'] if actual else None,
                'prediction_start': predicted[0]['month'] if predicted else None
            }
        }