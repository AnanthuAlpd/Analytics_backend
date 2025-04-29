from flask import Flask
from flask_cors import CORS
from db import init_db

# Import controllers
from controllers.user_controller import user_bp
from controllers.monthly_sales_stats_controller import monthly_stats_bp
from controllers.monthly_sales_stats_predicted_controller import monthly_stats_predicted_bp
from controllers.line_chart_main_controller import sales_chart_bp


def create_app():
    app = Flask(__name__)
    CORS(app, supports_credentials=True)
    init_db(app)

    # Register blueprints
    app.register_blueprint(user_bp)
    app.register_blueprint(monthly_stats_bp)
    app.register_blueprint(monthly_stats_predicted_bp)
    app.register_blueprint(sales_chart_bp)

    return app
