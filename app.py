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
from controllers.department_controller import department_bp
from controllers.services_controller import service_bp
from controllers.pr_monthly_sales_controller import pr_sales_dashboard
from controllers.client_controller import clients_bp
from controllers.login_controller import login_bp
def create_app():
    app = Flask(__name__)
    #CORS(app, supports_credentials=True)
    CORS(app, origins=['http://localhost:4200'])
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
    app.register_blueprint(sales_chart_bp, url_prefix='/api')
    app.register_blueprint(product_bp, url_prefix='/api')
    app.register_blueprint(employee_bp, url_prefix='/api')
    app.register_blueprint(department_bp, url_prefix='/api')
    app.register_blueprint(service_bp, url_prefix='/api')
    app.register_blueprint(pr_sales_dashboard, url_prefix='/api')
    app.register_blueprint(clients_bp, url_prefix='/api')
    app.register_blueprint(login_bp, url_prefix='/api')
    return app
