from datetime import timedelta
from flask import Flask, render_template, request, json, jsonify
from flask_cors import CORS
from db import init_db
from flask_jwt_extended import JWTManager
from werkzeug.middleware.proxy_fix import ProxyFix


# Import controllers

from controllers.line_chart_main_controller import sales_chart_bp
from controllers.product_controller import product_bp
from controllers.api_root_controller import api_root_bp
from controllers.emp_controller import employee_bp
from controllers.services_controller import service_bp
from controllers.pr_monthly_sales_controller import pr_sales_dashboard
from controllers.client_controller import clients_bp
from controllers.login_controller import login_bp
from controllers.leads_controller import leads_bp
from controllers.super_admin_controller import super_admin_bp
from controllers.demo_dashboard_controller import demo_dashboard_bp
from controllers.aswims.users_controller import user_bp
from controllers.business_analytics_controller import business_analytics_bp
from controllers.expense_controller import expense_bp
from controllers.aswims.patient_controller import patient_bp
from controllers.aswims.appointment_controller import appointments_bp
from controllers.aswims.specialities_controller import speciality_bp
from controllers.visitor_controller import visitor_bp
# Import controllers
def create_app():
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)
    
    CORS(app, origins=['http://localhost:4200', 'http://127.0.0.1:5500', 'http://localhost:5500', 'http://pothansai.com', 'https://www.pothansai.com', 'http://www.pothansai.com', 'https://pothansai.com'])
    init_db(app)

    # Background tasks
    from flask_apscheduler import APScheduler
    from tasks import check_and_update_overdue_leads
    scheduler = APScheduler()
    scheduler.init_app(app)
    
    # Run the lead update script automatically every night at midnight (production-ready)
    @scheduler.task('cron', id='update_overdue_leads_daily', hour=0, minute=0)
    def run_lead_updater():
        check_and_update_overdue_leads(app)
        
    scheduler.start()

    app.config['JWT_SECRET_KEY'] = 'ananthu'  # keep this secret!
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=7)

    jwt = JWTManager(app)

    # Register blueprints
    app.register_blueprint(api_root_bp, url_prefix='/api') # Adjust prefix as needed
    app.register_blueprint(sales_chart_bp, url_prefix='/api')
    app.register_blueprint(product_bp, url_prefix='/api')
    app.register_blueprint(employee_bp, url_prefix='/api')
    app.register_blueprint(service_bp, url_prefix='/api')
    app.register_blueprint(pr_sales_dashboard, url_prefix='/api')
    app.register_blueprint(clients_bp, url_prefix='/api')
    app.register_blueprint(login_bp, url_prefix='/api')
    app.register_blueprint(leads_bp, url_prefix='/api')
    app.register_blueprint(super_admin_bp, url_prefix='/api')
    app.register_blueprint(demo_dashboard_bp, url_prefix='/api')
    app.register_blueprint(appointments_bp, url_prefix='/api/aswims')
    app.register_blueprint(speciality_bp, url_prefix='/api/aswims')
    app.register_blueprint(user_bp,url_prefix='/api/aswims')
    app.register_blueprint(patient_bp,url_prefix='/api/aswims')
    app.register_blueprint(expense_bp, url_prefix='/api')
    app.register_blueprint(business_analytics_bp, url_prefix='/api')
    
    from controllers.budget_shopper_controller import budget_shopper_bp
    app.register_blueprint(budget_shopper_bp, url_prefix='/api')
    app.register_blueprint(visitor_bp, url_prefix='/api')

    import models


    @app.after_request
    def global_response_standardizer(response):
        # Skip 'aswims' and static content
        if request.path.startswith('/api/aswims') or not request.path.startswith('/api'):
            return response

        # Only wrap successful JSON responses that aren't already standardized
        # (Status codes 200-299)
        if 200 <= response.status_code < 300 and response.is_json:
            try:
                data = response.get_json()
                # Check if it already has our standard structure (all standard responses have a 'status' key)
                if not (isinstance(data, dict) and 'status' in data):
                    standardized_data = {
                        "status": "success",
                        "message": "Processed successfully",
                        "data": data
                    }
                    response.set_data(json.dumps(standardized_data))
            except Exception:
                # If JSON parsing fails for some reason, return the original response
                pass
        
        return response

    # Global Error Handling for Standardization
    from services.base_service import BaseService

    @app.errorhandler(Exception)
    def handle_global_exception(e):
        # Skip 'aswims' error standardization if needed, but usually good to have everywhere
        if request.path.startswith('/api/aswims'):
            return jsonify({"error": str(e)}), getattr(e, 'code', 500)

        # Standard handling using BaseService
        error_msg = str(e)
        code = 500
        if hasattr(e, 'code'):
            code = e.code
        
        # Log the error
        app.logger.error(f"Unhandled Exception: {error_msg}")
        
        return BaseService.create_response(
            message=error_msg,
            status="error",
            code=code
        )

    @app.route('/')
    def home():
        return render_template('index.html')

    return app
