from functools import wraps

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash

import database

auth_bp = Blueprint('auth', __name__)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'customer_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if session.get('customer_id'):
            return redirect(url_for('dashboard.dashboard'))
        return render_template('login.html')

    # POST
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()

    if not username or not password:
        flash('Username and password are required.', 'danger')
        return render_template('login.html')

    customer = database.get_customer_by_username(username)

    if not customer or not check_password_hash(customer['password_hash'], password):
        flash('Invalid username or password.', 'danger')
        return render_template('login.html')

    session['customer_id'] = customer['id']
    session['customer_name'] = customer['display_name']
    flash(f"Welcome back, {customer['display_name']}!", 'success')
    return redirect(url_for('dashboard.dashboard'))


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
