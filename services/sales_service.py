from models.actual_sales import ActualSales
from models.predicted_sales import PredictedSales

class SalesService:

    @staticmethod
    def get_sales_comparison_table():
        return ActualSales.get_comparison_table()
    
    @staticmethod
    def get_monthly_comparison(product_id=None, months=None):
        try:
            # Log inputs for debugging
            #print(f"Fetching monthly comparison with product_id={product_id} and months={months}")

            # Get actual sales data
            actual = [ActualSales.to_dict(row) for row in ActualSales.get_monthly_totals(product_id, months)]
            #print(f"Actual sales data: {actual}")  # Log the actual sales data

            # Get predicted sales data
            predicted = [PredictedSales.to_dict(row) for row in PredictedSales.get_monthly_totals(product_id, months)]
            #print(f"Predicted sales data: {predicted}")  # Log the predicted sales data

            max_product = PredictedSales.get_max_forecasted_product()
            valuable_product = PredictedSales.get_max_valuable_product()
            total_revenue=PredictedSales.get_total_revenue()

            # Prepare the response
            result = {
                'actual': actual,
                'predicted': predicted,
                'metadata': {
                    'actual_start': actual[0]['month'] if actual else None,
                    'actual_end': actual[-1]['month'] if actual else None,
                    'prediction_start': predicted[0]['month'] if predicted else None,
                    
                },
                'max_qty': max_product,
                'valuable_product' :  valuable_product,
                'total_revenue' : total_revenue              
            }

            # Log the final result
            #print(f"Final comparison result: {result}")

            return result

        except Exception as e:
            # Log the error if any exception occurs
            print(f"Error fetching monthly comparison: {e}")
            raise  # Reraise the exception after logging it
       