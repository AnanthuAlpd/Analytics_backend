from db import db
from datetime import datetime

class DemoSaleStats(db.Model):
    __tablename__ = 'monthly_sales_stats'
    
    stats_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'), nullable=False)
    report_date = db.Column(db.Date, nullable=True)
    total_quantity_sold = db.Column(db.Integer, nullable=True)
    total_revenue = db.Column(db.Numeric(10, 2), nullable=True)
    created_at = db.Column(db.TIMESTAMP, nullable=False, default=datetime.utcnow)
    stock_purchased = db.Column(db.Integer, nullable=True, default=0)
    opening_stock = db.Column(db.Integer, nullable=True, default=0)
    closing_stock = db.Column(db.Integer, nullable=False, default=0)
    
    # Relationship with Product
    product = db.relationship('Products', backref=db.backref('sales_stats', lazy=True))
    
    def to_dict(self):
        """Convert sales stats object to dictionary for JSON response"""
        return {
            'stats_id': self.stats_id,
            'product_id': self.product_id,
            'product_name': self.product.product_name if self.product else None,
            'report_date': self.report_date.isoformat() if self.report_date else None,
            'total_quantity_sold': self.total_quantity_sold,
            'total_revenue': float(self.total_revenue) if self.total_revenue else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'stock_purchased': self.stock_purchased,
            'opening_stock': self.opening_stock,
            'closing_stock': self.closing_stock
        }
    
    def __repr__(self):
        return f'<DemoSaleStats {self.report_date} - Product {self.product_id}>'