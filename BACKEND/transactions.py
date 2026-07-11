from flask import Blueprint, request, redirect, url_for, flash, session

import database
from auth import login_required

transactions_bp = Blueprint('transactions', __name__)


def parse_amount(raw):
    """Convert a raw form string to a positive float, or return None.

    Returns the float value if raw is a valid number greater than zero.
    Returns None for empty strings, non-numeric input, zero, or negatives.
    This function never raises — all conversion errors are caught internally.
    """
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
    """Handle a deposit request.

    Validates that the submitted amount is a positive number, then adds it
    to the customer's current balance and persists the result. Uses the
    Post/Redirect/Get pattern to prevent duplicate submissions on refresh.
    """
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
    """Handle a withdrawal request.

    Applies three sequential validation checks before touching the database:
      1. The amount field must not be empty.
      2. The amount must be a valid positive number.
      3. The amount must not exceed the customer's current balance.

    The balance is always read fresh from the database — it is never trusted
    from the session or from any browser-supplied value. Uses the
    Post/Redirect/Get pattern to prevent duplicate submissions on refresh.
    """
    raw = request.form.get('amount', '').strip()

    # Validation 1 — Presence check.
    # Catches a completely empty submission before attempting any numeric
    # conversion. The HTML 'required' attribute is a convenience only;
    # this server-side check is the authoritative guard.
    if not raw:
        flash('Amount is required', 'danger')
        return redirect(url_for('dashboard.dashboard'))

    amount = parse_amount(raw)

    # Validation 2 — Numeric and range check.
    # parse_amount returns None for non-numeric strings (e.g. "abc"),
    # zero, and negative values. All three cases are invalid withdrawal
    # amounts and are rejected here with the same user-facing message.
    if amount is None:
        flash('Amount must be greater than zero', 'danger')
        return redirect(url_for('dashboard.dashboard'))

    # Read the current balance fresh from the database.
    # Never rely on a balance value from the session or the request —
    # always query the DB immediately before the balance check.
    customer_id = session['customer_id']
    account = database.get_account_by_customer_id(customer_id)
    current_balance = account['balance']

    # Validation 3 — Sufficient funds check.
    # The requested withdrawal must not exceed the available balance.
    # The current balance is included in the error message so the customer
    # knows exactly how much they have without navigating away.
    if amount > current_balance:
        flash(f'Insufficient funds. Your balance is ${current_balance:.2f}.', 'danger')
        return redirect(url_for('dashboard.dashboard'))

    new_balance = current_balance - amount
    database.update_balance(customer_id, new_balance)

    flash(f'Successfully withdrew ${amount:.2f}. New balance: ${new_balance:.2f}', 'success')
    return redirect(url_for('dashboard.dashboard'))