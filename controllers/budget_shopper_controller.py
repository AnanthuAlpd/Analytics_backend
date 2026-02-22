from flask import Blueprint, request
from services.budget_shopper_service import BudgetShopperService

budget_shopper_bp = Blueprint('budget_shopper', __name__)

@budget_shopper_bp.route('/optimize-budget', methods=['POST'])
def optimize_budget():
    data = request.get_json() or {}
    budget = data.get('budget', 0)
    months_coverage = data.get('months_coverage', 6)
    
    return BudgetShopperService.optimize_budget(budget, months_coverage)
