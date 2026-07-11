from flask import Blueprint, render_template, session
from auth import login_required
import database

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    customer_id = session.get('customer_id')
    account = database.get_account_by_customer_id(customer_id)
    balance = account['balance'] if account is not None else 0.0
    customer_name = session.get('customer_name', 'Customer')
    return render_template('dashboard.html', customer_name=customer_name, balance=balance)
