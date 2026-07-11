from flask import Blueprint, request, redirect, url_for, flash, session

import database
from auth import login_required

transactions_bp = Blueprint('transactions', __name__)


def parse_amount(raw):
    """Convert a raw form string to a positive float, or return None."""
    try:
        value = float(raw)
    except (ValueError, TypeError):
        return None
    if value <= 0.0:
        return None
    return value


@transactions_bp.route('/deposit', methods=['POST'])
@login_required
def deposit():
    raw = request.form.get('amount', '').strip()
    amount = parse_amount(raw)

    if amount is None:
        flash('Please enter a valid amount greater than zero.', 'danger')
        return redirect(url_for('dashboard.dashboard'))

    customer_id = session['customer_id']
    account = database.get_account_by_customer_id(customer_id)
    new_balance = account['balance'] + amount
    database.update_balance(customer_id, new_balance)

    flash(f'Successfully deposited ${amount:.2f}. New balance: ${new_balance:.2f}', 'success')
    return redirect(url_for('dashboard.dashboard'))


@transactions_bp.route('/withdraw', methods=['POST'])
@login_required
def withdraw():
    raw = request.form.get('amount', '').strip()
    amount = parse_amount(raw)

    if amount is None:
        flash('Please enter a valid amount greater than zero.', 'danger')
        return redirect(url_for('dashboard.dashboard'))

    customer_id = session['customer_id']
    account = database.get_account_by_customer_id(customer_id)
    current_balance = account['balance']

    if amount > current_balance:
        flash(f'Insufficient funds. Your balance is ${current_balance:.2f}.', 'danger')
        return redirect(url_for('dashboard.dashboard'))

    new_balance = current_balance - amount
    database.update_balance(customer_id, new_balance)

    flash(f'Successfully withdrew ${amount:.2f}. New balance: ${new_balance:.2f}', 'success')
    return redirect(url_for('dashboard.dashboard'))
