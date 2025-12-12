from db import db
from datetime import datetime

class MonthlySalesStatsPredicted(db.Model):
    __tablename__ = 'monthly_sales_stats_predicted'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    product_id = db.Column(db.BigInteger, db.ForeignKey('product.product_id'), nullable=True)
    report_date = db.Column(db.DateTime, nullable=True)
    forecasted_quantity = db.Column(db.Float, nullable=True)
    best_model = db.Column(db.Text, nullable=True)
    
    # Relationship with Product
    product = db.relationship('Products', backref=db.backref('predicted_sales', lazy=True))
    
    def to_dict(self):
        """Convert predicted sales object to dictionary for JSON response"""
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product.product_name if self.product else None,
            'report_date': self.report_date.isoformat() if self.report_date else None,
            'forecasted_quantity': self.forecasted_quantity,
            'best_model': self.best_model
        }
    
    def __repr__(self):
        return f'<MonthlySalesStatsPredicted {self.report_date} - Product {self.product_id}>'