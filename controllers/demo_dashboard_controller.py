from flask import Blueprint, current_app,request,jsonify
from services.base_service import BaseService
from services.demo_dashboard_service import DemoDashboardService
import traceback
# from utils.base_service import BaseService
# from services.dashboard_service import DashboardService

demo_dashboard_bp = Blueprint('dashboard', __name__)

@demo_dashboard_bp.route('/demo-dashboard/kpi', methods=['GET'])

def get_kpi_data():
    try:
        kpi_data=DemoDashboardService.get_kpi_card_data()
        return BaseService.create_response(
            data=kpi_data,
            message="KPI data fetched successfully",
            status="success",
            code=200
        )
    except Exception as e:
        current_app.logger.error(f"Server error: {str(e)}")
        return BaseService.create_response(
            message="Internal server error",
            status="error",
            code=500
        )

@demo_dashboard_bp.route('/demo-dashboard/monthly-comparison')
def monthly_comparison():
    product_id = request.args.get('product_id', type=int)
    months = request.args.get('months', type=int)

    return jsonify(
        DemoDashboardService.get_monthly_comparison(product_id, months)
    )

# def get_kpi_data():
#     try:
#         # Fetch KPI data without filters
#         kpi_data = DemoDashboardService.get_kpi_data()
#         return BaseService.create_response(
#             data=kpi_data,
#             message="KPI data fetched successfully",
#             status="success",
#             code=200
#         )

#     except Exception as e:
#         current_app.logger.error(f"Server error: {str(e)}")
#         return BaseService.create_response(
#             message="Internal server error",
#             status="error",
#             code=500
#         )

@demo_dashboard_bp.route('/demo-dashboard/sales-trend', methods=['GET'])
def get_sales_trend():
    try:
        # Fetch KPI data without filters
        product_id = request.args.get('product_id', type=int)
        result = DemoDashboardService.get_sales_trend(product_id)
        return BaseService.create_response(
            data=result,
            message="Sale trend data fetched successfully for line chart",
            status="success",
            code=200
        )

    except Exception as e:
        current_app.logger.error(f"Server error: {str(e)}")
        return BaseService.create_response(
            message="Internal server error",
            status="error",
            code=500
        )



@demo_dashboard_bp.route('/demo-dashboard/product-comparison', methods=['GET'])
def get_top_product_comparison():
    try:
        # Fetch KPI data with optional product filter
        product_id = request.args.get('product_id', type=int)
        result = DemoDashboardService.get_top_product_comparison(product_id)
        return BaseService.create_response(
            data=result,
            message="product comparison data fetched successfully for line chart",
            status="success",
            code=200
        )

    except Exception as e:
        current_app.logger.error(f"Server error: {str(e)}")
        return BaseService.create_response(
            message="Internal server error",
            status="error",
            code=500
        )

@demo_dashboard_bp.route('/demo-dashboard/product-comparison-total', methods=['GET'])
def get_total_product_comparison():
    try:
        # Fetch KPI data without filters
        product_id = request.args.get('product_id', type=int)
        result = DemoDashboardService.get_total_actual_vs_predicted(product_id)
        return BaseService.create_response(
            data=result,
            message="total product comparison data fetched successfully- bar chart",
            status="success",
            code=200
        )

    except Exception as e:
        current_app.logger.error(f"Server error: {str(e)}")
        return BaseService.create_response(
            message="Internal server error",
            status="error",
            code=500
        )


@demo_dashboard_bp.route('/demo-dashboard/product-growth', methods=['GET'])
def get_product_growth_performance():
    try:
        # Fetch KPI data without filters
        #product_id = request.args.get('product_id', type=int)
        result = DemoDashboardService.get_product_growth_performance()
        return BaseService.create_response(
            data=result,
            message="product growth performance data fetched successfully for line chart",
            status="success",
            code=200
        )

    except Exception as e:
        current_app.logger.error(f"Server error: {str(e)}")
        return BaseService.create_response(
            message="Internal server error",
            status="error",
            code=500
        )

@demo_dashboard_bp.route('/demo-dashboard/product-summary', methods=['GET'])
def get_forecast_summary():
    try:
        # Fetch KPI data without filters
        #product_id = request.args.get('product_id', type=int)
        result = DemoDashboardService.get_forecast_summary()
        return BaseService.create_response(
            data=result,
            message="product summary data fetched successfully for line chart",
            status="success",
            code=200
        )

    except Exception as e:
        # 1. Get the full traceback as a string
        full_traceback = traceback.format_exc()

        # 2. Log the full traceback instead of just str(e)
        # This gives you the file name, line number, and function calls that led to the error.
        current_app.logger.error(f"Server Error with Full Traceback:\n{full_traceback}")

        # 3. Return the *generic* client response (best practice)
        # The client doesn't need the traceback, but you need it for debugging.
        return BaseService.create_response(
            message="Internal server error", 
            status="error",
            code=500
        )

@demo_dashboard_bp.route('/demo-dashboard/products', methods=['GET'])
def get_products_list():
    try:
        products = DemoDashboardService.get_products()
        return BaseService.create_response(
            data=products,
            message="Products fetched successfully",
            status="success",
            code=200
        )
    except Exception as e:
        current_app.logger.error(f"Error fetching products: {str(e)}")
        return BaseService.create_response(
            message="Internal server error",
            status="error",
            code=500
        )
   