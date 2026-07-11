"""
Integration tests for the banking web application.

Uses Flask's built-in test client and an isolated temporary SQLite database
so the real BACKEND/banking.db is never touched during test runs.

Strategy:
  1. Override `database.DB_PATH` to a temp file before importing `app`.
  2. Call `database.init_db()` with the temp DB — this seeds one test user
     (testuser / password123, balance 1000.00).
  3. Each test that needs an authenticated session logs in first via the
     test client.
"""

import sys
import os
import tempfile
import pytest

# ---------------------------------------------------------------------------
# Make BACKEND importable
# ---------------------------------------------------------------------------
BACKEND_DIR = os.path.join(os.path.dirname(__file__), '..', 'BACKEND')
sys.path.insert(0, os.path.abspath(BACKEND_DIR))


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def app_client():
    """
    Yield a Flask test client backed by a fresh temporary database.

    The fixture:
      - Creates a temp SQLite file.
      - Patches database.DB_PATH to point at it.
      - Calls init_db() to create tables and seed testuser.
      - Yields the test client with TESTING=True and a stable secret key.
      - Deletes the temp file on teardown.
    """
    import database

    # Create an isolated temp DB file
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)

    # Override the module-level path before any connection is opened
    original_path = database.DB_PATH
    database.DB_PATH = db_path

    # Seed the temp database
    database.init_db()

    # Now import (or re-use) the app — it will use the patched DB_PATH
    import app as flask_app

    flask_app.app.config['TESTING'] = True
    flask_app.app.config['SECRET_KEY'] = 'test-secret'

    with flask_app.app.test_client() as client:
        yield client

    # Teardown: restore original path and delete temp file
    database.DB_PATH = original_path
    try:
        os.unlink(db_path)
    except OSError:
        pass


def _login(client, username='testuser', password='password123'):
    """Helper: POST to /login and follow the redirect."""
    return client.post(
        '/login',
        data={'username': username, 'password': password},
        follow_redirects=True,
    )


# ---------------------------------------------------------------------------
# Authentication tests
# ---------------------------------------------------------------------------

class TestAuthentication:

    def test_valid_login_redirects_to_dashboard(self, app_client):
        """Correct credentials should land the user on the dashboard."""
        resp = _login(app_client)
        assert resp.status_code == 200
        assert b'Current Balance' in resp.data

    def test_invalid_password_stays_on_login(self, app_client):
        """Wrong password must not redirect; login page is returned."""
        resp = app_client.post(
            '/login',
            data={'username': 'testuser', 'password': 'wrongpassword'},
            follow_redirects=True,
        )
        assert resp.status_code == 200
        assert b'Invalid username or password' in resp.data

    def test_unknown_username_stays_on_login(self, app_client):
        """Non-existent username must show a generic error."""
        resp = app_client.post(
            '/login',
            data={'username': 'nobody', 'password': 'anything'},
            follow_redirects=True,
        )
        assert resp.status_code == 200
        assert b'Invalid username or password' in resp.data

    def test_empty_fields_shows_error(self, app_client):
        """Submitting blank fields should flash a validation error."""
        resp = app_client.post(
            '/login',
            data={'username': '', 'password': ''},
            follow_redirects=True,
        )
        assert resp.status_code == 200
        assert b'required' in resp.data.lower()

    def test_logout_clears_session(self, app_client):
        """After logout, visiting /dashboard must redirect to /login."""
        _login(app_client)
        app_client.get('/logout', follow_redirects=True)
        resp = app_client.get('/dashboard', follow_redirects=True)
        assert b'Sign In' in resp.data  # login page marker


# ---------------------------------------------------------------------------
# Session guard tests
# ---------------------------------------------------------------------------

class TestSessionGuard:

    def test_unauthenticated_dashboard_redirects(self, app_client):
        """A fresh client (no session) must be redirected to /login."""
        resp = app_client.get('/dashboard', follow_redirects=True)
        assert resp.status_code == 200
        assert b'Sign In' in resp.data

    def test_unauthenticated_deposit_redirects(self, app_client):
        """POSTing to /deposit without a session must redirect to /login."""
        resp = app_client.post('/deposit', data={'amount': '100'}, follow_redirects=True)
        assert b'Sign In' in resp.data

    def test_unauthenticated_withdraw_redirects(self, app_client):
        """POSTing to /withdraw without a session must redirect to /login."""
        resp = app_client.post('/withdraw', data={'amount': '100'}, follow_redirects=True)
        assert b'Sign In' in resp.data


# ---------------------------------------------------------------------------
# Transaction tests
# ---------------------------------------------------------------------------

class TestTransactions:

    def test_deposit_increases_balance(self, app_client):
        """A valid deposit should show an increased balance on the dashboard."""
        _login(app_client)
        resp = app_client.post('/deposit', data={'amount': '250'}, follow_redirects=True)
        assert resp.status_code == 200
        assert b'1250.00' in resp.data

    def test_withdraw_decreases_balance(self, app_client):
        """A valid withdrawal should show a decreased balance on the dashboard."""
        _login(app_client)
        resp = app_client.post('/withdraw', data={'amount': '200'}, follow_redirects=True)
        assert resp.status_code == 200
        assert b'800.00' in resp.data

    def test_withdraw_full_balance_gives_zero(self, app_client):
        """Withdrawing the exact balance should result in $0.00."""
        _login(app_client)
        resp = app_client.post('/withdraw', data={'amount': '1000'}, follow_redirects=True)
        assert resp.status_code == 200
        assert b'0.00' in resp.data

    def test_overdraft_is_rejected(self, app_client):
        """Withdrawing more than the balance must flash an error and leave balance unchanged."""
        _login(app_client)
        resp = app_client.post('/withdraw', data={'amount': '9999'}, follow_redirects=True)
        assert resp.status_code == 200
        assert b'Insufficient funds' in resp.data
        # Balance must remain at original 1000.00
        assert b'1000.00' in resp.data

    def test_invalid_deposit_amount_shows_error(self, app_client):
        """Non-numeric deposit input must flash a validation error."""
        _login(app_client)
        resp = app_client.post('/deposit', data={'amount': 'abc'}, follow_redirects=True)
        assert b'valid amount' in resp.data

    def test_zero_deposit_shows_error(self, app_client):
        """Zero deposit must be rejected."""
        _login(app_client)
        resp = app_client.post('/deposit', data={'amount': '0'}, follow_redirects=True)
        assert b'valid amount' in resp.data
