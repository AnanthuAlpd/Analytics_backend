from models.pr_monthly_sales import MonthlySales
from models.pr_product_master import Product
from models.clients import Client
from db import db
from sqlalchemy import func
from datetime import date

def get_april_summary(client_id):
    start = date(2025, 4, 1)
    end = date(2025, 4, 30)

    # Total revenue for this client
    total_value = db.session.query(
        func.sum(Product.unit_cost * MonthlySales.qty_sold)
    ).select_from(MonthlySales)\
     .join(Product, Product.product_id == MonthlySales.product_id)\
     .filter(MonthlySales.report_date.between(start, end))\
     .filter(MonthlySales.client_id == client_id)\
     .scalar()

    # Highest selling product by quantity for this client
    top = db.session.query(
        Product.name,
        Product.hsn_no,
        func.sum(MonthlySales.qty_sold).label('total_qty')
    ).select_from(MonthlySales)\
     .join(Product, Product.product_id == MonthlySales.product_id)\
     .filter(MonthlySales.report_date.between(start, end))\
     .filter(MonthlySales.client_id == client_id)\
     .group_by(Product.name, Product.hsn_no)\
     .order_by(func.sum(MonthlySales.qty_sold).desc())\
     .limit(1).first()

    # Top revenue generating product for this client
    top_revenue = db.session.query(
        Product.name,
        Product.hsn_no,
        func.sum(Product.unit_cost * MonthlySales.qty_sold).label('total_revenue')
    ).select_from(MonthlySales)\
     .join(Product, Product.product_id == MonthlySales.product_id)\
     .filter(MonthlySales.report_date.between(start, end))\
     .filter(MonthlySales.client_id == client_id)\
     .group_by(Product.name, Product.hsn_no)\
     .order_by(func.sum(Product.unit_cost * MonthlySales.qty_sold).desc())\
     .limit(1).first()

    return {
        "total_sales_value": round(total_value or 0, 2),
        "highest_selling_product": {
            "name": top[0] if top else None,
            "hsn": top[1] if top else None,
            "units_sold": int(top[2]) if top else 0
        },
        "top_revenue_product": {
            "name": top_revenue[0] if top_revenue else None,
            "hsn": top_revenue[1] if top_revenue else None,
            "revenue": round(top_revenue[2], 2) if top_revenue else 0
        }
    }

def get_top_10_selling_products(client_id):
    start = date(2025, 4, 1)
    end = date(2025, 4, 30)

    results = db.session.query(
        Product.name,
        Product.hsn_no,
        func.sum(MonthlySales.qty_sold).label("value")
    ).join(Product, Product.product_id == MonthlySales.product_id)\
     .filter(MonthlySales.report_date.between(start, end))\
     .filter(MonthlySales.client_id == client_id)\
     .group_by(Product.product_id, Product.name, Product.hsn_no)\
     .order_by(func.sum(MonthlySales.qty_sold).desc())\
     .limit(10)\
     .all()

    # Combine name and hsn_no for ngx-charts
    chart_data = [{
        "name": f"{row.name} ({row.hsn_no})",
        "value": int(row.value)
    } for row in results]

    return chart_data

def get_top_10_revenue_products(client_id):
    start = date(2025, 4, 1)
    end = date(2025, 4, 30)

    results = db.session.query(
        Product.name,
        Product.hsn_no,
        func.sum(Product.unit_cost * MonthlySales.qty_sold).label("value")
    ).select_from(MonthlySales)\
    .join(Product, Product.product_id == MonthlySales.product_id)\
     .filter(MonthlySales.report_date.between(start, end))\
     .filter(MonthlySales.client_id==client_id)\
     .group_by(Product.product_id, Product.name, Product.hsn_no)\
     .order_by(func.sum(Product.unit_cost * MonthlySales.qty_sold).desc())\
     .limit(10)\
     .all()

    chart_data = [{
        "name": f"{row.name} ({row.hsn_no})",
        "value": float(round(row.value, 2))
    } for row in results]

    return chart_data

def get_least_selling_products(client_id,limit=10):
    start = date(2025, 4, 1)
    end = date(2025, 4, 30)

    results = db.session.query(
        Product.product_id,
        Product.name,
        Product.hsn_no,
        Product.unit,
        func.sum(MonthlySales.qty_sold).label("qty")
    ).select_from(MonthlySales)\
    .join(Product, Product.product_id == MonthlySales.product_id)\
    .filter(MonthlySales.report_date.between(start, end))\
    .filter(MonthlySales.client_id==client_id)\
    .group_by(Product.product_id, Product.name, Product.hsn_no, Product.unit)\
    .having(func.sum(MonthlySales.qty_sold) > 0)\
    .order_by(func.sum(MonthlySales.qty_sold))\
    .limit(limit).all()

    tableData= [{
        "name": row.name,
        "hsn": row.hsn_no,
        "unit": row.unit,
        "qty": int(row.qty)
    } for row in results]

    return tableData


def get_unsold_products(client_id):
    start = date(2025, 4, 1)
    end = date(2025, 4, 30)

    # Subquery: sum of qty_sold per product for April
    subq = db.session.query(
        MonthlySales.product_id,
        func.sum(MonthlySales.qty_sold).label('total_qty')
    ).filter(
        MonthlySales.report_date.between(start, end)
    ).filter(
        MonthlySales.client_id==client_id
    ).group_by(MonthlySales.product_id).subquery()

    # Outer query: left join to find products with no or zero sales
    results = db.session.query(
        Product.product_id,
        Product.name,
        Product.hsn_no,
        Product.unit,
        subq.c.total_qty
    ).outerjoin(
        subq, subq.c.product_id == Product.product_id
    ).filter(
        (subq.c.total_qty == None) | (subq.c.total_qty == 0)
    ).all()

    # Format results for JSON
    unsold_list = [{
        "name": row.name,
        "hsn": row.hsn_no,
        "unit": row.unit
    } for row in results]

    return unsold_list

def get_low_performance_products(client_id,threshold=10, limit=10):
    start = date(2025, 4, 1)
    end = date(2025, 4, 30)

    results = db.session.query(
        Product.name,
        Product.hsn_no,
        Product.unit,
        func.sum(MonthlySales.qty_sold).label("qty")
    ).join(Product, Product.product_id == MonthlySales.product_id)\
     .filter(MonthlySales.report_date.between(start, end))\
     .filter(MonthlySales.client_id==client_id)\
     .group_by(Product.product_id, Product.name, Product.hsn_no, Product.unit)\
     .having(func.sum(MonthlySales.qty_sold) < threshold)\
     .order_by(func.sum(MonthlySales.qty_sold))\
     .limit(limit).all()

    return [{
        "name": row.name,
        "hsn": row.hsn_no,
        "unit": row.unit,
        "qty": int(row.qty)
    } for row in results]
    
def get_top_valued_products(client_id,limit=10):
    results = db.session.query(
        Product.name,
        Product.hsn_no,
        Product.unit,
        Product.unit_cost
    ).filter(Product.client_id==client_id
    ).order_by(Product.unit_cost.desc())\
     .limit(limit).all()

    return [{
        "name": row.name,
        "hsn": row.hsn_no,
        "unit": row.unit,
        "rate": float(row.unit_cost)
    } for row in results]


