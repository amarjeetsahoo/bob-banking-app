# Banking Web Application — Build Plan

> **Reference docs:** IMPLEMENTATION_PLAN.md, STEP_BY_STEP_IMPLEMENTATION_GUIDE.md  
> **Status:** Pending implementation  
> **Goal:** Build the full-stack banking app incrementally, one focused subtask at a time.

---

## Top-Level Overview

Build a local, browser-based banking application using:
- **Frontend:** HTML + Bootstrap (Jinja2 templates) in `FRONTEND/`
- **Backend:** Python Flask in `BACKEND/`
- **Database:** SQLite (`BACKEND/banking.db`)

Features: customer login, dashboard, view balance, deposit, withdraw, logout.

Each subtask below maps to one self-contained phase. Complete and verify each before moving to the next.

---

## Subtask 1 — Project Scaffolding & Environment Files

**Status:** [ ] pending

**Intent:**  
Create the directory skeleton, `.gitignore`, and `requirements.txt`. No application logic yet — just the foundation that all future subtasks depend on.

**Expected Outcomes:**
- `FRONTEND/templates/` and `FRONTEND/static/` directories exist
- `BACKEND/` directory exists with `requirements.txt` listing Flask
- `.gitignore` excludes `venv/`, `__pycache__/`, `*.pyc`, and `BACKEND/banking.db`
- `README.md` exists at project root with basic run instructions placeholder

**Todo List:**
1. Create `FRONTEND/templates/` directory (place a `.gitkeep` if empty)
2. Create `FRONTEND/static/` directory (place a `.gitkeep` if empty)
3. Create `BACKEND/requirements.txt` with `Flask` and `Werkzeug` listed
4. Create `.gitignore` covering `venv/`, `__pycache__/`, `*.pyc`, `*.pyo`, `BACKEND/banking.db`
5. Create `README.md` with project title, tech stack, and a "How to Run" section skeleton

**Relevant Context:**
- Folder structure defined in IMPLEMENTATION_PLAN.md §4
- `banking.db` must never be committed — gitignore it here

---

## Subtask 2 — Database Module (`database.py`)

**Status:** [ ] pending

**Intent:**  
Implement the entire data access layer before any routes exist. All SQL lives here. Routes will only ever call named functions from this module.

**Expected Outcomes:**
- `BACKEND/database.py` exists
- `get_connection()` opens `banking.db` with a row_factory so columns are accessible by name
- `init_db()` creates `customers` table (id, username, password_hash, display_name) and `accounts` table (id, customer_id, balance) using `CREATE TABLE IF NOT EXISTS`
- `init_db()` seeds one test customer (`testuser` / `password123`) with a Werkzeug-hashed password and a starting balance of `1000.00` if no customers exist
- `get_customer_by_username(username)` returns a single customer row or None
- `get_account_by_customer_id(customer_id)` returns the account row for that customer
- `update_balance(customer_id, new_balance)` writes the new balance and commits

**Todo List:**
1. Create `BACKEND/database.py`
2. Write `get_connection()` — builds path from `__file__`, sets `row_factory = sqlite3.Row`
3. Write `init_db()` — `CREATE TABLE IF NOT EXISTS` for both tables, then seed check + insert
4. Write `get_customer_by_username(username)` — SELECT by username, return one row
5. Write `get_account_by_customer_id(customer_id)` — SELECT by customer_id, return one row
6. Write `update_balance(customer_id, new_balance)` — UPDATE accounts, commit

**Relevant Context:**
- Guide §2.2: row_factory, `__file__`-based path, idempotent init
- Guide §4.3: why path must be relative to `database.py` not the working directory
- Werkzeug: `generate_password_hash()` for seeding, `check_password_hash()` used in auth.py

---

## Subtask 3 — Flask App Entry Point (`app.py`)

**Status:** [ ] pending

**Intent:**  
Wire together the Flask application instance with correct template/static paths, secret key, DB initialisation, and route registrations. This is the single file that `flask run` executes.

**Expected Outcomes:**
- `BACKEND/app.py` exists and starts without error
- Flask resolves templates from `../FRONTEND/templates` relative to `app.py`
- Flask resolves static files from `../FRONTEND/static`
- `init_db()` is called once at startup (inside `with app.app_context()` or equivalent)
- A root redirect (`/`) sends browsers to `/login`
- Running `python app.py` or `flask run` starts the dev server on port 5000

**Todo List:**
1. Create `BACKEND/app.py`
2. Construct absolute paths to `FRONTEND/templates` and `FRONTEND/static` using `os.path`
3. Create Flask app instance with `template_folder` and `static_folder` pointing to those paths
4. Set `app.secret_key` to a development string
5. Call `init_db()` at startup
6. Add a root route `/` that redirects to `/login`
7. Add `if __name__ == '__main__': app.run(debug=True)` guard

**Relevant Context:**
- Guide §2.1: app.py responsibilities
- Guide §4.1: why template_folder must be explicit
- Blueprint/module registration happens in Subtask 4 (auth) and Subtask 5 (dashboard + transactions)

---

## Subtask 4 — Authentication Module (`auth.py` + `login.html`)

**Status:** [ ] pending

**Intent:**  
Implement login, logout, and the session guard decorator. This is the security boundary for the entire application.

**Expected Outcomes:**
- `BACKEND/auth.py` exists with `/login` (GET + POST) and `/logout` routes registered on a Blueprint named `auth`
- `FRONTEND/templates/login.html` exists and extends `layout.html`
- GET `/login` renders the login form; redirects to `/dashboard` if already logged in
- POST `/login` validates credentials, sets `session['customer_id']` and `session['customer_name']` on success, flashes generic error on failure
- `/logout` clears the session and redirects to `/login`
- `login_required` decorator is defined in `auth.py` and importable by other modules
- `app.py` registers the `auth` blueprint

**Todo List:**
1. Create `BACKEND/auth.py` with a Flask Blueprint named `auth`
2. Implement GET `/login` — check session, render template or redirect
3. Implement POST `/login` — read form, query DB, verify hash, set session, redirect or flash+render
4. Implement GET `/logout` — `session.clear()`, redirect to `/login`
5. Implement `login_required` decorator — checks `session.get('customer_id')`, redirects if missing
6. Create `FRONTEND/templates/layout.html` — full HTML shell, Bootstrap CDN, navbar with conditional Logout link, flash message loop, content block
7. Create `FRONTEND/templates/login.html` — extends layout, centred Bootstrap card, username + password inputs, submit button, form posts to `/login`
8. Register `auth` blueprint in `app.py`

**Relevant Context:**
- Guide §2.3: exact POST login logic flow, generic error message requirement
- Guide §3.1: layout.html structure, flash message rendering pattern
- Guide §3.2: login.html Bootstrap card layout
- Session fields stored: `customer_id` (int), `customer_name` (str)

---

## Subtask 5 — Dashboard Module (`dashboard.py` + `dashboard.html`)

**Status:** [ ] pending

**Intent:**  
Build the authenticated landing page. After this subtask a logged-in customer can see their name and balance. The transaction forms will be wired in Subtask 6.

**Expected Outcomes:**
- `BACKEND/dashboard.py` exists with a Blueprint named `dashboard`
- GET `/dashboard` is protected by `login_required`
- Route reads `customer_id` from session, fetches account balance from DB, renders template
- `FRONTEND/templates/dashboard.html` shows a personalised greeting and current balance
- Placeholder Deposit and Withdraw buttons/sections are visible (forms wired in next subtask)
- `app.py` registers the `dashboard` blueprint

**Todo List:**
1. Create `BACKEND/dashboard.py` with a Flask Blueprint named `dashboard`
2. Implement GET `/dashboard` — `@login_required`, read session, call `get_account_by_customer_id()`, render template with `customer_name` and `balance`
3. Create `FRONTEND/templates/dashboard.html` — extends layout, Bootstrap container, greeting card, balance display card, placeholder sections for deposit/withdraw forms
4. Register `dashboard` blueprint in `app.py`

**Relevant Context:**
- Guide §2.4: dashboard route logic
- Guide §3.3: dashboard template layout — greeting, balance card, two-column grid
- `login_required` imported from `auth.py`

---

## Subtask 6 — Transaction Module (`transactions.py`) + Wire Forms in Dashboard

**Status:** [ ] pending

**Intent:**  
Implement deposit and withdrawal business logic, and complete the dashboard template with working forms. After this subtask the full feature set is functional end-to-end.

**Expected Outcomes:**
- `BACKEND/transactions.py` exists with a Blueprint named `transactions`
- POST `/deposit` validates amount, updates balance, flashes success, redirects to `/dashboard`
- POST `/withdraw` validates amount, checks funds, updates balance or flashes error, redirects to `/dashboard`
- `dashboard.html` updated with working deposit form (posts to `/deposit`) and withdraw form (posts to `/withdraw`)
- Both forms use `type="number"` with `min="0.01"` and `step="0.01"` and `required`
- Deposit button uses `btn-success`, withdraw button uses `btn-danger`
- `app.py` registers the `transactions` blueprint

**Todo List:**
1. Create `BACKEND/transactions.py` with a Flask Blueprint named `transactions`
2. Implement POST `/deposit` — `@login_required`, read amount, server-side validate (non-empty, numeric, > 0), fetch balance, add amount, call `update_balance()`, flash success, redirect
3. Implement POST `/withdraw` — `@login_required`, read amount, server-side validate, fetch balance, check sufficiency, subtract or flash "Insufficient funds", redirect
4. Update `FRONTEND/templates/dashboard.html` — replace placeholder sections with real deposit and withdraw forms
5. Register `transactions` blueprint in `app.py`

**Relevant Context:**
- Guide §2.5: full deposit and withdrawal step-by-step logic, Post/Redirect/Get explanation
- Guide §5.3 and §5.4: all validation rules for both operations
- Guide §3.4 and §3.5: form HTML attributes and button colour conventions

---

## Subtask 7 — Custom Styles (`style.css`)

**Status:** [ ] pending

**Intent:**  
Add minimal project-specific CSS to improve visual polish beyond default Bootstrap. Keep this small — Bootstrap utilities should handle 90% of layout.

**Expected Outcomes:**
- `FRONTEND/static/style.css` exists
- Balance display card has a visually distinct background or accent
- Login card is centred vertically on the page with adequate top margin
- The stylesheet is linked from `layout.html`

**Todo List:**
1. Create `FRONTEND/static/style.css` with targeted rules for the balance card and login page centering
2. Add a `<link>` tag in `layout.html` `<head>` pointing to `{{ url_for('static', filename='style.css') }}`

**Relevant Context:**
- Guide §3.6: Bootstrap utilities are preferred; CSS is for overrides only
- Flask's `url_for('static', filename=...)` generates the correct path regardless of where flask runs from

---

## Subtask 8 — Unit Tests

**Status:** [ ] pending

**Intent:**  
Write isolated unit tests for the three pure-logic concerns: password hashing, amount parsing, and balance arithmetic. No Flask server or database required.

**Expected Outcomes:**
- `tests/` directory exists at project root
- `tests/test_unit.py` covers password hash/verify, valid/invalid amount parsing, and deposit/withdraw arithmetic
- All tests pass with `pytest` from the project root

**Todo List:**
1. Create `tests/` directory with `__init__.py` (empty)
2. Create `tests/test_unit.py`
3. Write test for `generate_password_hash` + `check_password_hash` round-trip (correct and wrong password)
4. Write tests for amount validation logic: valid float string, empty string, letters, zero, negative number
5. Write tests for balance arithmetic: deposit increases balance, withdraw decreases balance, withdraw exactly at balance produces zero
6. Add `pytest` to `BACKEND/requirements.txt`

**Relevant Context:**
- Guide §6.1: what to unit test and how to structure tests
- Amount validation logic lives in `transactions.py` — extract it to a named helper function so it can be imported and tested in isolation

---

## Subtask 9 — Integration Tests

**Status:** [ ] pending

**Intent:**  
Test all five critical end-to-end flows using Flask's test client and an in-memory database. These tests verify that routes, session management, and DB writes all work together correctly.

**Expected Outcomes:**
- `tests/test_integration.py` exists
- Tests cover: login success, login failure, unauthenticated dashboard redirect, deposit, withdraw (success), withdraw (insufficient funds), logout + session cleared
- Tests use an in-memory SQLite database — `banking.db` is never touched
- All tests pass with `pytest`

**Todo List:**
1. Create `tests/test_integration.py`
2. Write a pytest fixture that creates the Flask test client with `TESTING=True` and an in-memory DB
3. Write test: valid login → redirects to `/dashboard`
4. Write test: invalid login → stays on `/login` with error in response
5. Write test: unauthenticated GET `/dashboard` → redirects to `/login`
6. Write test: login + POST `/deposit` valid amount → balance increases on dashboard
7. Write test: login + POST `/withdraw` valid amount → balance decreases
8. Write test: login + POST `/withdraw` exceeds balance → error flash, balance unchanged
9. Write test: login + GET `/logout` → session cleared, subsequent `/dashboard` redirects to `/login`

**Relevant Context:**
- Guide §6.2: Flask test client pattern, in-memory DB, TESTING flag
- `database.py` must accept an injectable DB path or the app config must allow overriding it for the test fixture to work

---

## Subtask 10 — README & Final Verification

**Status:** [ ] pending

**Intent:**  
Complete the `README.md` with accurate run instructions, and do a final end-to-end manual verification pass using the checklist from the implementation guide.

**Expected Outcomes:**
- `README.md` contains: prerequisites, virtual environment setup steps, install command, how to run (`flask run`), default login credentials, how to run tests
- Manual testing checklist from Guide §6.3 passes for all 24 items
- No raw Python errors or stack traces visible in the browser under normal use

**Todo List:**
1. Rewrite `README.md` with complete, accurate run instructions matching the actual project structure
2. Include the default seed credentials (`testuser` / `password123`) in README
3. Include the `pytest` command in README
4. Perform manual walkthrough: login → view balance → deposit → withdraw → overdraft error → logout → back-button test
5. Confirm all 24 checklist items from Guide §6.3 pass

**Relevant Context:**
- Guide §7.1: exact local run steps to document
- Seed credentials are defined in `database.py` Subtask 2

---

## Dependency Order

```
Subtask 1  (Scaffolding)
    └── Subtask 2  (database.py)
            └── Subtask 3  (app.py)
                    └── Subtask 4  (auth.py + login.html)
                            └── Subtask 5  (dashboard.py + dashboard.html)
                                    └── Subtask 6  (transactions.py + forms)
                                            └── Subtask 7  (style.css)
                                            └── Subtask 8  (unit tests)
                                                    └── Subtask 9  (integration tests)
                                                            └── Subtask 10  (README + verification)
```
