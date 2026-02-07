from flask import Blueprint, current_app, request
from services.base_service import BaseService
from services.business_analytics_service import BusinessAnalyticsService
import traceback

business_analytics_bp = Blueprint('business_analytics', __name__)

@business_analytics_bp.route('/business-analytics/revenue-metrics', methods=['GET'])
def get_revenue_metrics():
    """Get comprehensive revenue and profit metrics"""
    try:
        metrics = BusinessAnalyticsService.get_revenue_metrics()
        return BaseService.create_response(
            data=metrics,
            message="Revenue metrics fetched successfully",
            status="success",
            code=200
        )
    except Exception as e:
        current_app.logger.error(f"Error fetching revenue metrics: {str(e)}")
        return BaseService.create_response(
            message="Internal server error",
            status="error",
            code=500
        )

@business_analytics_bp.route('/business-analytics/category-performance', methods=['GET'])
def get_category_performance():
    """Get sales performance breakdown by category"""
    try:
        data = BusinessAnalyticsService.get_category_performance()
        return BaseService.create_response(
            data=data,
            message="Category performance data fetched successfully",
            status="success",
            code=200
        )
    except Exception as e:
        current_app.logger.error(f"Error fetching category performance: {str(e)}")
        return BaseService.create_response(
            message="Internal server error",
            status="error",
            code=500
        )

@business_analytics_bp.route('/business-analytics/revenue-trend', methods=['GET'])
def get_revenue_trend():
    """Get monthly revenue and profit trend"""
    try:
        months = request.args.get('months', default=12, type=int)
        data = BusinessAnalyticsService.get_revenue_trend(months)
        return BaseService.create_response(
            data=data,
            message="Revenue trend data fetched successfully",
            status="success",
            code=200
        )
    except Exception as e:
        current_app.logger.error(f"Error fetching revenue trend: {str(e)}")
        return BaseService.create_response(
            message="Internal server error",
            status="error",
            code=500
        )

@business_analytics_bp.route('/business-analytics/alerts', methods=['GET'])
def get_business_alerts():
    """Get business alerts and warnings"""
    try:
        alerts = BusinessAnalyticsService.get_business_alerts()
        return BaseService.create_response(
            data=alerts,
            message="Business alerts fetched successfully",
            status="success",
            code=200
        )
    except Exception as e:
        full_traceback = traceback.format_exc()
        current_app.logger.error(f"Error fetching business alerts:\n{full_traceback}")
        return BaseService.create_response(
            message="Internal server error",
            status="error",
            code=500
        )

@business_analytics_bp.route('/business-analytics/top-performers', methods=['GET'])
def get_top_performers():
    """Get top performing products"""
    try:
        limit = request.args.get('limit', default=5, type=int)
        data = BusinessAnalyticsService.get_top_performers(limit)
        return BaseService.create_response(
            data=data,
            message="Top performers fetched successfully",
            status="success",
            code=200
        )
    except Exception as e:
        current_app.logger.error(f"Error fetching top performers: {str(e)}")
        return BaseService.create_response(
            message="Internal server error",
            status="error",
            code=500
        )
