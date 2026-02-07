from db import db
from datetime import datetime


class MonthlySalesStats(db.Model):
    __tablename__ = 'mas_monthly_sales_stats'

    stats_id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    report_date = db.Column(
        db.Date,
        nullable=False
    )

    product_id = db.Column(
        db.Integer,
        db.ForeignKey('products.product_id'),
        nullable=False,
        index=True   # because of MUL key
    )

    client_id = db.Column(
        db.Integer,
        db.ForeignKey('clients.client_id'),
        nullable=True,
        index=True   # because of MUL key
    )

    qty_sold = db.Column(
        db.Integer,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp()
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp()
    )

    def __repr__(self):
        return (
            f"<MonthlySalesStats "
            f"report_date={self.report_date}, "
            f"product_id={self.product_id}, "
            f"qty_sold={self.qty_sold}>"
        )
