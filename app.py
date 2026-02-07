from datetime import timedelta
from flask import Flask
from flask_cors import CORS
from db import init_db
from flask_jwt_extended import JWTManager


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
from controllers.aswims.patient_controller import patient_bp


from controllers.aswims.appointment_controller import appointments_bp
from controllers.aswims.specialities_controller import speciality_bp
from controllers.expense_controller import expense_bp
from controllers.business_analytics_controller import business_analytics_bp
#print("🔥 LOADED app.py FROM:", __file__)
def create_app():
    app = Flask(__name__)
    #print("🔥 create_app() CALLED")
    #CORS(app, supports_credentials=True)
    CORS(app) # Allow all origins for debugging
    init_db(app)

    app.config['JWT_SECRET_KEY'] = 'ananthu'  # keep this secret!
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=7)

    jwt = JWTManager(app)

    # Register blueprints
    #app.register_blueprint(user_bp, url_prefix='/api')
    #app.register_blueprint(monthly_stats_bp)
    #app.register_blueprint(monthly_stats_predicted_bp)
    #app.register_blueprint(sales_chart_bp)
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

     # 🔴 DEBUG: PRINT ROUTESu
    # print("\n=== REGISTERED ROUTES ===")
    # for rule in app.url_map.iter_rules():
    #     print(rule)
    # print("========================\n")
    import models
    return app
