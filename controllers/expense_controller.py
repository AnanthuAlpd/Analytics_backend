from flask import Blueprint, request, jsonify
from db import db
from models.expense_model import Expense
from sqlalchemy import func
from datetime import datetime, timedelta
from collections import defaultdict

expense_bp = Blueprint('expense_bp', __name__)

@expense_bp.route('/expenses', methods=['GET'])
def get_expenses():
    expenses = Expense.query.order_by(Expense.date.desc()).all()
    return jsonify([e.to_dict() for e in expenses])

@expense_bp.route('/expenses', methods=['POST'])
def add_expense():
    data = request.get_json()
    new_expense = Expense(
        description=data.get('description'),
        amount=float(data.get('amount')),
        type=data.get('type'),
        category=data.get('category'),
        date=data.get('date') # Assuming ISO string or None for default
    )
    db.session.add(new_expense)
    db.session.commit()
    return jsonify(new_expense.to_dict()), 201

@expense_bp.route('/expenses/<int:id>', methods=['PUT'])
def update_expense(id):
    expense = Expense.query.get_or_404(id)
    data = request.get_json()
    
    expense.description = data.get('description', expense.description)
    expense.amount = float(data.get('amount', expense.amount))
    expense.type = data.get('type', expense.type)
    expense.category = data.get('category', expense.category)
    
    db.session.commit()
    return jsonify(expense.to_dict())

@expense_bp.route('/expenses/<int:id>', methods=['DELETE'])
def delete_expense(id):
    expense = Expense.query.get_or_404(id)
    db.session.delete(expense)
    db.session.commit()
    return '', 204

@expense_bp.route('/summary', methods=['GET'])
def get_summary():
    try:
        # Calculate totals
        total_income = db.session.query(func.sum(Expense.amount)).filter(Expense.type == 'income').scalar() or 0
        total_expense = db.session.query(func.sum(Expense.amount)).filter(Expense.type == 'expense').scalar() or 0
        
        # Category breakdown for pie chart (expenses only)
        categories = db.session.query(
            Expense.category, 
            func.sum(Expense.amount)
        ).filter(Expense.type == 'expense').group_by(Expense.category).all()
        
        category_data = {str(cat): float(amt) for cat, amt in categories if cat is not None}
        
        return jsonify({
            'total_income': float(total_income),
            'total_expense': float(total_expense),
            'balance': float(total_income - total_expense),
            'categories': category_data
        })
    except Exception as e:
        print(f"Error in summary: {e}")
        return jsonify({'error': str(e)}), 500

@expense_bp.route('/expenses/trend', methods=['GET'])
def get_trend():
    period = request.args.get('period', 'monthly')
    limit = int(request.args.get('limit', 12 if period == 'monthly' else 7 if period == 'daily' else 4))
    
    try:
        # Calculate date range
        today = datetime.now().date()
        
        if period == 'daily':
            start_date = today - timedelta(days=limit - 1)
            date_format = '%b %d'
            delta = timedelta(days=1)
        elif period == 'weekly':
            start_date = today - timedelta(weeks=limit - 1)
            date_format = 'Week %U'
            delta = timedelta(weeks=1)
        else:  # monthly
            # Go back 'limit' months
            start_date = today.replace(day=1)
            for _ in range(limit - 1):
                start_date = (start_date - timedelta(days=1)).replace(day=1)
            date_format = '%b %Y'
            delta = None  # Handle monthly differently
        
        # Fetch expenses within date range
        expenses = Expense.query.filter(Expense.date >= start_date).all()
        
        # Aggregate data
        income_data = defaultdict(float)
        expense_data = defaultdict(float)
        
        for exp in expenses:
            if period == 'monthly':
                key = exp.date.strftime('%b %Y')
            elif period == 'weekly':
                key = f"Week {exp.date.strftime('%U')}"
            else:  # daily
                key = exp.date.strftime('%b %d')
            
            if exp.type == 'income':
                income_data[key] += exp.amount
            else:
                expense_data[key] += exp.amount
        
        # Generate labels for the period
        labels = []
        current = start_date
        
        if period == 'monthly':
            for i in range(limit):
                labels.append(current.strftime(date_format))
                # Move to next month
                if current.month == 12:
                    current = current.replace(year=current.year + 1, month=1)
                else:
                    current = current.replace(month=current.month + 1)
        else:
            for i in range(limit):
                if period == 'weekly':
                    labels.append(f"Week {current.strftime('%U')}")
                else:
                    labels.append(current.strftime(date_format))
                current += delta
        
        # Build response arrays
        income_values = [income_data.get(label, 0) for label in labels]
        expense_values = [expense_data.get(label, 0) for label in labels]
        
        return jsonify({
            'labels': labels,
            'income': income_values,
            'expenses': expense_values
        })
    except Exception as e:
        print(f"Error in trend: {e}")
        return jsonify({'error': str(e)}), 500
