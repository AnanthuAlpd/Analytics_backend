from flask import Blueprint, request, current_app
from services.visitor_service import VisitorService
from services.base_service import BaseService
import traceback

visitor_bp = Blueprint('visitor', __name__)

@visitor_bp.route('/public/visitor-count', methods=['GET'])
def get_visitor_count():
    """
    Public endpoint for tracking and fetching visitor counts.
    Detects IP automatically.
    """
    try:
        # Get IP address, handling potential proxy headers
        if request.headers.getlist("X-Forwarded-For"):
            ip_address = request.headers.getlist("X-Forwarded-For")[0]
        else:
            ip_address = request.remote_addr

        # Record visit and get updated count
        count = VisitorService.record_visit(ip_address)
        
        return BaseService.create_response(
            data={"count": count},
            message="Visitor count fetched successfully",
            status="success",
            code=200
        )
    except Exception as e:
        error_info = traceback.format_exc()
        current_app.logger.error(f"Error in get_visitor_count:\n{error_info}")
        return BaseService.create_response(
            message="Internal server error",
            status="error",
            code=500
        )
