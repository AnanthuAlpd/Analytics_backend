from db import db

class DemoDashboardCardSummary(db.Model):
    __tablename__ = 'demo_dashboard_summary'

    summary_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    year = db.Column(db.Integer, unique=True, nullable=True)
    summary_generated_at = db.Column(db.DateTime, nullable=True)
    
    # Sales Metrics
    total_products = db.Column(db.Integer, nullable=True)
    predicted_sales = db.Column(db.Numeric(15, 2), nullable=True)
    current_growth_rate = db.Column(db.Numeric(10, 2), nullable=True)
    predicted_growth_rate = db.Column(db.Numeric(10, 2), nullable=True)
    prediction_accuracy = db.Column(db.Numeric(10, 2), nullable=True)
    
    # Backorder Metrics
    total_backorder_qty = db.Column(db.Numeric(15, 2), nullable=True)
    yearly_avg_backorder = db.Column(db.Numeric(15, 2), nullable=True)
    monthly_avg_backorder = db.Column(db.Numeric(15, 2), nullable=True)
    products_with_backorder = db.Column(db.Integer, nullable=True)
    
    # Metadata
    backorder_data_start = db.Column(db.Date, nullable=True)
    backorder_data_end = db.Column(db.Date, nullable=True)
    total_months_analyzed = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())

    def __repr__(self):
        return f"<DemoDashboardSummary year={self.year}>"

    def to_dict(self):
        """
        Converts the model instance into a dictionary.
        Handles Date, DateTime, and Numeric serialization for JSON compatibility.
        """
        return {
            'summary_id': self.summary_id,
            'year': self.year,
            'summary_generated_at': self.summary_generated_at.isoformat() if self.summary_generated_at else None,
            
            # Integers
            'total_products': self.total_products,
            'products_with_backorder': self.products_with_backorder,
            'total_months_analyzed': self.total_months_analyzed,

            # Decimals (Converted to float for JSON)
            'predicted_sales': float(self.predicted_sales) if self.predicted_sales is not None else None,
            'current_growth_rate': float(self.current_growth_rate) if self.current_growth_rate is not None else None,
            'predicted_growth_rate': float(self.predicted_growth_rate) if self.predicted_growth_rate is not None else None,
            'prediction_accuracy': float(self.prediction_accuracy) if self.prediction_accuracy is not None else None,
            'total_backorder_qty': float(self.total_backorder_qty) if self.total_backorder_qty is not None else None,
            'yearly_avg_backorder': float(self.yearly_avg_backorder) if self.yearly_avg_backorder is not None else None,
            'monthly_avg_backorder': float(self.monthly_avg_backorder) if self.monthly_avg_backorder is not None else None,

            # Dates
            'backorder_data_start': self.backorder_data_start.isoformat() if self.backorder_data_start else None,
            'backorder_data_end': self.backorder_data_end.isoformat() if self.backorder_data_end else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }