from models.pr_product_master import Product
from db import db
from sqlalchemy import or_
from datetime import date

def get_client_products(client_id, search_term=None):
    query = db.session.query(
        Product.product_id,
        Product.name,
        Product.hsn_no
    ).filter(Product.client_id == client_id)

    if search_term:
        like_term = f"%{search_term}%"
        query = query.filter(or_(
            Product.name.ilike(like_term),
            Product.hsn_no.ilike(like_term)
        ))

    return query.order_by(Product.name).limit(50).all()