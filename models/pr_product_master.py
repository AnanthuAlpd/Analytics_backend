from db import db

class Product(db.Model):
    __tablename__ = 'products'

    product_id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer)
    hsn_no = db.Column(db.String(20))
    name = db.Column(db.String(100), nullable=False)
    unit = db.Column(db.String(20))
    unit_cost = db.Column(db.Numeric(10, 2))
