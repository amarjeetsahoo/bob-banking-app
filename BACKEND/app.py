import os

from flask import Flask, redirect, url_for

import database
from auth import auth_bp
from dashboard import dashboard_bp
from transactions import transactions_bp

# ---------------------------------------------------------------------------
# Path construction
# ---------------------------------------------------------------------------
_base_dir       = os.path.dirname(os.path.abspath(__file__))
template_folder = os.path.join(_base_dir, '..', 'FRONTEND', 'templates')
static_folder   = os.path.join(_base_dir, '..', 'FRONTEND', 'static')

# ---------------------------------------------------------------------------
# Flask application instance
# ---------------------------------------------------------------------------
app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
app.secret_key = 'dev-secret-key-change-in-production'

# ---------------------------------------------------------------------------
# Database initialisation — safe to call on every startup (idempotent)
# ---------------------------------------------------------------------------
try:
    database.init_db()
except Exception as e:
    print(f'[app] database.init_db() failed: {e}')

# ---------------------------------------------------------------------------
# Blueprint registration
# ---------------------------------------------------------------------------
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(transactions_bp)

# ---------------------------------------------------------------------------
# Root redirect
# ---------------------------------------------------------------------------
@app.route('/')
def index():
    return redirect(url_for('auth.login'))


if __name__ == '__main__':
    app.run(debug=True)
