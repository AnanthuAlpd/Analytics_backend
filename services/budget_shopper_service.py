from services.base_service import BaseService
from models.demo_products import Products
from models.demo_sale_stats import DemoSaleStats
from db import db
from sqlalchemy import func

class BudgetShopperService(BaseService):
    
    @staticmethod
    def optimize_budget(budget_amount, months_coverage):
        try:
            budget = float(budget_amount)
            months = int(months_coverage)

            if budget <= 0:
                return BaseService.create_response(status="error", message='Invalid budget amount', code=400)

            # Create a subquery to aggregate the sales data per product
            sales_subq = db.session.query(
                DemoSaleStats.product_id,
                func.avg(DemoSaleStats.total_quantity_sold).label('avg_monthly_sales'),
                func.max(DemoSaleStats.closing_stock).label('latest_stock')
            ).group_by(DemoSaleStats.product_id).subquery()

            # Join Products to the aggregated sales subquery
            products_query = db.session.query(
                Products,
                sales_subq.c.avg_monthly_sales,
                sales_subq.c.latest_stock
            ).outerjoin(
                sales_subq, Products.product_id == sales_subq.c.product_id
            ).all()

            analyzed_products = []

            # Analyze and Forecast
            for product, avg_monthly_sales, latest_stock in products_query:
                if not avg_monthly_sales or not product.cost_price:
                    continue

                avg_sales = float(avg_monthly_sales)
                cost_price = float(product.cost_price)
                current_stock = int(latest_stock) if latest_stock else 0

                # 1. ENHANCED QUERY: Get selling_price to calculate margin
                sale_price = float(product.sale_price) if getattr(product, 'sale_price', None) else cost_price * 1.2

                # 2. CALCULATE PROFIT PER UNIT
                profit_per_unit = sale_price - cost_price

                forecasted_need = avg_sales * months

                # Bypassing current_stock for Demo Data purposes:
                purchasing_need = max(1, int(forecasted_need))

                if purchasing_need > 0:
                    # 3. ADVANCED EBO SCORE
                    # Score = (Monthly Revenue * Profit Margin) / Cost
                    monthly_revenue = avg_sales * sale_price
                    score = (monthly_revenue * profit_per_unit) / cost_price

                    analyzed_products.append({
                        'product_id': product.product_id,
                        'name': product.product_name,
                        'unit_cost': cost_price,
                        'unit_profit': round(profit_per_unit, 2),
                        'avg_monthly_sales': round(avg_sales, 1),
                        'current_stock': current_stock,
                        'purchasing_need': purchasing_need,
                        'score': score,
                        'recommended_qty': 0,
                        'subtotal': 0
                    })

            # Sort by ROI Score (Descending)
            analyzed_products.sort(key=lambda x: x['score'], reverse=True)

            shopping_list = []
            total_cost = 0
            current_budget = budget

            # Greedy Allocation
            for item in analyzed_products:
                if current_budget <= 0:
                    break

                total_cost_for_need = item['purchasing_need'] * item['unit_cost']

                if current_budget >= total_cost_for_need:
                    # Afford full 6-month requirement
                    item['recommended_qty'] = item['purchasing_need']
                    item['subtotal'] = total_cost_for_need
                    current_budget -= total_cost_for_need
                else:
                    # Afford partial restock
                    possible_qty = int(current_budget // item['unit_cost'])
                    if possible_qty > 0:
                        item['recommended_qty'] = possible_qty
                        item['subtotal'] = possible_qty * item['unit_cost']
                        current_budget -= item['subtotal']

                if item['recommended_qty'] > 0:
                    shopping_list.append(item)
                    total_cost += item['subtotal']

            response_data = {
                'budget_provided': budget,
                'months_coverage': months,
                'total_investment': total_cost,
                'remaining_budget': current_budget,
                'shopping_list': shopping_list
            }
            
            return BaseService.create_response(data=response_data, message="Budget optimized successfully")

        except Exception as e:
            import traceback
            traceback.print_exc()
            return BaseService.create_response(status="error", message=str(e), code=500)
