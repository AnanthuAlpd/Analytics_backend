from app import create_app
from services.demo_dashboard_service import DemoDashboardService
import json

app = create_app()
with app.app_context():
    print("--- Testing Default (Top 10) ---")
    res_default = DemoDashboardService.get_product_growth_performance()
    print(json.dumps(res_default[:2], indent=2)) # Show first 2 products
    
    print("\n--- Testing Specific Product (ID: 1) ---")
    res_single = DemoDashboardService.get_product_growth_performance(product_id=1)
    print(json.dumps(res_single, indent=2))
