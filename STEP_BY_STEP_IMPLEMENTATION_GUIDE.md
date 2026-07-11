# Banking Web Application — Step-by-Step Implementation Guide

> **Reference:** IMPLEMENTATION_PLAN.md  
> **Purpose:** Plain-English instructions explaining *how* to build each part of the application — the logic, the decisions, and the sequence. No raw code is included.

---

## Table of Contents

1. [Environment Setup](#1-environment-setup)
2. [Backend Implementation](#2-backend-implementation)
3. [Frontend Implementation](#3-frontend-implementation)
4. [Integration Steps](#4-integration-steps)
5. [Validation Rules](#5-validation-rules)
6. [Testing](#6-testing)
7. [Deployment](#7-deployment)

---

## 1. Environment Setup

### 1.1 Prerequisites

Before writing a single line of application code, confirm the following tools are installed on your machine:

- **Python 3.9 or later** — Flask requires a modern Python version. Verify by running the Python version command in your terminal.
- **pip** — Python's package manager, bundled with Python. Used to install Flask and related libraries.
- **A terminal** — PowerShell (Windows), Terminal (macOS/Linux), or any shell you are comfortable with.
- **A code editor** — VS Code is recommended but any editor works.

### 1.2 Create a Virtual Environment

A virtual environment isolates this project's dependencies from other Python projects on your machine. This prevents version conflicts.

- Navigate into the project root directory in your terminal.
- Use Python's built-in `venv` module to create a new virtual environment inside the project. Name the folder something clear, such as `venv`.
- **Activate** the virtual environment. The activation command differs by operating system — on Windows it is a script in the `Scripts` subfolder; on macOS/Linux it is in the `bin` subfolder.
- Once activated, your terminal prompt will change to show the environment name, confirming all subsequent `pip install` commands will install into this isolated environment.
- Add the `venv/` folder to `.gitignore` so it is never committed to source control.

### 1.3 Install Dependencies

With the virtual environment active, install the required packages:

- **Flask** — the web framework that handles routing, templates, and sessions.
- **Werkzeug** — installed automatically with Flask; provides password hashing utilities.
- No other third-party libraries are needed for this application.

After installing, create `BACKEND/requirements.txt` by freezing the current environment. This file allows any other developer (or a CI pipeline) to reproduce the exact same dependency set with a single install command.

### 1.4 Confirm Flask Is Working

Create a minimal `BACKEND/app.py` that does only one thing: starts a Flask application and returns a plain text response on the root URL. Run `flask run` from inside the `BACKEND/` directory. If a browser visit to `http://127.0.0.1:5000` shows your placeholder response, the environment is correctly configured and you can proceed.

---

## 2. Backend Implementation

### 2.1 Application Entry Point (`app.py`)

`app.py` is the heart of the Flask application. Its responsibilities are:

- **Create the Flask app instance.** This is the object that everything else registers against.
- **Set a secret key.** Flask uses this to cryptographically sign session cookies. For development, a hardcoded string is acceptable. For production this must be a random, secret value stored outside the codebase.
- **Tell Flask where to find templates.** Because templates live in `FRONTEND/templates/` rather than the default `templates/` folder, you must explicitly pass the template folder path when creating the app instance.
- **Tell Flask where to find static files.** Similarly, point Flask at `FRONTEND/static/`.
- **Register all route modules.** Import the auth, dashboard, and transaction modules and register their routes (or blueprints) with the app.
- **Initialise the database.** Call the database initialisation function once at startup to ensure the tables and seed data exist before the first request arrives.
- **Start the development server.** The `app.run()` call at the bottom (inside an `if __name__ == '__main__'` guard) starts the server when the file is run directly.

### 2.2 Database Module (`database.py`)

This module is the only place in the application that talks to SQLite directly. All other modules call functions defined here rather than writing SQL themselves.

**Connection helper:**  
Write a function that opens a connection to `banking.db` inside the `BACKEND/` folder. The connection should return rows as dictionary-like objects (SQLite supports a `row_factory` setting for this) so you can access columns by name rather than by index. This makes the rest of the code far more readable.

**Initialisation function:**  
Write a function that, when called, checks whether the `customers` and `accounts` tables already exist and creates them if they do not. This is safe to call every time the app starts — it will not destroy existing data. After creating the tables, check whether any seed customer exists. If not, insert one test customer with a securely hashed password and create a corresponding account record with a starting balance.

**Query helpers (optional but recommended):**  
Consider writing two small utility functions — one that executes a query and returns all matching rows, and one that executes a write query (INSERT, UPDATE) and commits the change. Centralising these prevents you from forgetting to commit after writes or from accidentally leaving connections open.

### 2.3 Authentication Module (`auth.py`)

This module handles the `/login` (GET and POST) and `/logout` routes.

**GET `/login`:**  
Simply render the login HTML template. If the customer is already logged in (their user ID is already in the session), redirect them straight to the dashboard — there is no need to show the login form to someone who is already authenticated.

**POST `/login`:**  
This is where the actual authentication logic lives:

1. Read the submitted username and password from the incoming form data.
2. Query the database for a customer record whose username matches the submitted value.
3. If no record is found, flash a generic error message ("Invalid username or password") and re-render the login page. Do not say "username not found" — that reveals too much.
4. If a record is found, use Werkzeug's password-check utility to compare the submitted plaintext password against the stored hash. Werkzeug handles the hashing algorithm internally — you never need to write your own.
5. If the password check passes, write the customer's database ID and display name into the Flask session object. Then redirect to the dashboard.
6. If the password check fails, flash the same generic error and re-render the login page.

**`/logout`:**  
Clear all data from the Flask session object and redirect the customer to the login page.

**Session guard (login-required decorator):**  
Write a reusable Python decorator (a function that wraps other functions) that:
1. Checks whether a customer ID exists in the current session.
2. If not, redirects the request to the login page.
3. If yes, allows the original route function to run.

Apply this decorator to every route that should be protected — dashboard, deposit, and withdraw.

### 2.4 Dashboard Module (`dashboard.py`)

This module handles a single route: GET `/dashboard`.

- Apply the login-required decorator to protect this route.
- Read the customer's ID from the session.
- Call the database module to retrieve the customer's display name and current account balance.
- Pass both values to the `dashboard.html` template for rendering.
- Flask's template rendering function handles injecting the data into the HTML and returning the final page to the browser.

### 2.5 Transaction Module (`transactions.py`)

This module handles POST `/deposit` and POST `/withdraw`.

**Deposit logic:**
1. Apply the login-required decorator.
2. Read the submitted amount from the form data.
3. Validate the amount (see Section 5 for rules). If invalid, flash an error and redirect back to the dashboard without touching the database.
4. Convert the validated amount to a decimal number.
5. Retrieve the current balance from the database for the logged-in customer.
6. Add the deposit amount to the current balance.
7. Write the new balance back to the database.
8. Flash a success message.
9. Redirect to the dashboard. The redirected GET request to the dashboard will then fetch and display the updated balance.

**Withdrawal logic:**
1. Apply the login-required decorator.
2. Read and validate the submitted amount (same validation as deposit).
3. Retrieve the current balance from the database.
4. Check whether the current balance is greater than or equal to the requested withdrawal amount. If not, flash an "insufficient funds" error and redirect to the dashboard without writing anything.
5. If sufficient funds exist, subtract the withdrawal amount from the balance.
6. Write the new balance to the database.
7. Flash a success message.
8. Redirect to the dashboard.

**Why redirect after POST?**  
This pattern (called Post/Redirect/Get) prevents the browser from re-submitting the form if the user refreshes the page after a transaction. Always redirect after a successful or failed POST rather than rendering a template directly.

### 2.6 Session Management

Flask sessions work by serialising the session dictionary into a signed cookie stored in the browser. The signing uses the app's secret key, so the data cannot be tampered with by the client without detection.

Key points to understand:
- You interact with the session exactly like a Python dictionary — read from it, write to it, and delete from it.
- Storing the customer's database ID in the session is sufficient to identify them on every subsequent request.
- Never store the customer's password (even hashed) in the session — the ID is all you need.
- The session is automatically cleared when `session.clear()` is called (at logout).
- Session cookies are scoped to the browser tab's domain and port; they will not persist across different origins.

### 2.7 Error Handling

For this workshop application, error handling should be simple and predictable:

- **Invalid form input** — Caught at the route level before any database call. Flash a descriptive message and redirect.
- **Insufficient funds** — Caught in the withdrawal route after reading the balance. Flash a message and redirect without writing.
- **Unauthenticated access** — Caught by the login-required decorator. Redirect to login.
- **Database errors** — For a local SQLite application, these should not occur under normal use. Do not add complex try/except blocks for scenarios that cannot realistically happen in this context.
- **404 Not Found** — Flask handles this automatically. No custom handler is needed for this scope.

---

## 3. Frontend Implementation

All templates live in `FRONTEND/templates/` and are Jinja2 templates rendered by Flask. Jinja2 allows you to embed Python-like expressions and control flow directly inside HTML using `{{ }}` for values and `{% %}` for logic.

### 3.1 Base Layout (`layout.html`)

This is the master template that all other pages extend. It should contain:

- The full HTML document structure (`<html>`, `<head>`, `<body>`).
- The Bootstrap CSS link loaded from a CDN inside `<head>`. No local installation is required.
- A Bootstrap navbar at the top. The navbar should conditionally show a "Logout" link only when the user is logged in. Use a Jinja2 `if` block to check whether the customer's name is in the session.
- A `<main>` content block that child templates override to inject their specific content.
- A block for displaying flash messages. Place this just inside the `<main>` area so it appears on every page without being repeated in each template.

**Flash message rendering:**  
Flask provides a `get_flashed_messages()` function that is available inside all Jinja2 templates. Loop over the messages and render each one inside a Bootstrap alert `<div>`. Messages should disappear after one page load — Flask handles this automatically by removing messages from the queue once they are read.

### 3.2 Login Page (`login.html`)

This template extends `layout.html` and overrides the content block with:

- A centred Bootstrap card or panel to visually frame the login form.
- A heading such as "Welcome to Online Banking".
- A form with two inputs: username (text) and password (password type).
- A submit button styled with a Bootstrap primary button class.
- The form's action attribute must point to the Flask `/login` URL and use the POST method.
- No JavaScript validation is needed on this form — the backend handles all credential validation.

### 3.3 Dashboard Page (`dashboard.html`)

This template extends `layout.html` and is only ever rendered for authenticated customers. It should contain:

- A personalised greeting using the customer's display name passed from the Flask route (rendered with `{{ customer_name }}`).
- A prominent balance display — a Bootstrap card or jumbotron-style container showing the current balance formatted as a currency value.
- Two action sections side by side (use Bootstrap's grid columns): one for depositing and one for withdrawing.
- Each action section contains a small form with a numeric input field and a submit button.
- The deposit form posts to `/deposit` and the withdraw form posts to `/withdraw`.
- A logout button or link that points to `/logout`.

### 3.4 Deposit Form

The deposit form lives inside `dashboard.html`. It should:

- Accept only positive numeric input. Use the HTML `input` element with `type="number"` and set the `min` attribute to a value greater than zero to trigger browser-level validation.
- Have a clear label ("Deposit Amount") and placeholder text.
- Use a Bootstrap success-coloured button to visually distinguish it from the withdraw action.

### 3.5 Withdraw Form

The withdraw form mirrors the deposit form but with different semantics:

- Use a Bootstrap warning or danger-coloured button to signal that this action reduces the balance.
- The `min` attribute on the numeric input should also prevent zero or negative values at the browser level.
- Server-side validation is still the authoritative check — the HTML attributes are a convenience, not a security measure.

### 3.6 Bootstrap Layout Principles

Throughout all templates, follow these conventions:

- Wrap page content in a Bootstrap `container` div to keep it centred and responsive.
- Use Bootstrap's `row` and `col` grid classes to lay out side-by-side elements such as the two transaction forms.
- Use `mb-*` and `mt-*` spacing utilities for vertical spacing rather than custom CSS where possible.
- Use Bootstrap `alert` classes for flash messages. The `alert-success` class for confirmations and `alert-danger` for errors create an immediately understandable visual hierarchy.
- Use `form-control` on all form inputs and `btn btn-*` on all buttons for consistent styling.

---

## 4. Integration Steps

### 4.1 Connect Flask to Templates

Flask needs to know that your templates are in `FRONTEND/templates/` rather than the default location. When creating the Flask app instance in `app.py`, pass the `template_folder` argument pointing to that path relative to `app.py`. Do the same for `static_folder` pointing to `FRONTEND/static/`. Once this is configured, Flask's `render_template()` function will look in the correct directory automatically.

### 4.2 Connect Forms to Routes

Each HTML form must have two attributes set correctly for Flask to receive the data:

- `action` — the URL path that the form submits to (for example `/login`, `/deposit`, or `/withdraw`).
- `method` — should be `POST` for all forms that submit data.

The `name` attribute on each `<input>` element is the key Flask uses to retrieve the submitted value from `request.form`. Make sure the names in your HTML match exactly what the Flask route reads using `request.form.get('field_name')`.

### 4.3 Connect Flask to SQLite

The `database.py` module manages the connection. The path to `banking.db` should be constructed relative to the `database.py` file itself (not relative to wherever `flask run` is called from). Python's `__file__` variable gives the absolute path of the currently executing file, which you can use to build a reliable path to the database file regardless of the working directory.

Every route that reads or writes data should call functions from `database.py`. The route itself should not contain any SQL strings — it should only call named functions like `get_account_balance(customer_id)` or `update_balance(customer_id, new_balance)`. This separation keeps route logic clean and makes the data layer easy to change or test independently.

### 4.4 Connect Session to Database

When a customer logs in, their database-assigned ID is stored in the session. Every subsequent request to a protected route reads this ID back from the session and uses it to scope all database queries to that specific customer. This ID-based approach means:

- You never need to re-authenticate on every request.
- All balance queries automatically return only that customer's account.
- Logging out simply removes the ID from the session, making all protected routes inaccessible until login occurs again.

---

## 5. Validation Rules

### 5.1 Login Validation

| Rule | Where Enforced | Behaviour on Failure |
|---|---|---|
| Username field must not be empty | Server (Flask route) | Flash error, re-render login page |
| Password field must not be empty | Server (Flask route) | Flash error, re-render login page |
| Username must exist in the database | Server (database lookup) | Flash generic error, re-render login page |
| Password must match stored hash | Server (Werkzeug check) | Flash generic error, re-render login page |

> **Security note:** Always use the same generic error message ("Invalid username or password") regardless of which check failed. Never reveal whether the username exists or only the password was wrong.

### 5.2 Balance Validation

| Rule | Where Enforced | Behaviour on Failure |
|---|---|---|
| Balance must never go below zero | Server (withdrawal route) | Flash "Insufficient funds", redirect to dashboard, no DB write |
| Balance is always read from the database | Server | Never trust a balance value sent from the browser |

### 5.3 Deposit Validation

| Rule | Where Enforced | Behaviour on Failure |
|---|---|---|
| Amount field must not be empty | Server + HTML `required` attribute | Flash error / browser prevents submission |
| Amount must be a valid number | Server (parse attempt) | Flash error, redirect to dashboard |
| Amount must be greater than zero | Server + HTML `min` attribute | Flash error / browser prevents submission |

### 5.4 Withdrawal Validation

| Rule | Where Enforced | Behaviour on Failure |
|---|---|---|
| Amount field must not be empty | Server + HTML `required` attribute | Flash error / browser prevents submission |
| Amount must be a valid number | Server (parse attempt) | Flash error, redirect to dashboard |
| Amount must be greater than zero | Server + HTML `min` attribute | Flash error / browser prevents submission |
| Amount must not exceed current balance | Server (balance check) | Flash "Insufficient funds", redirect, no DB write |

> **Important:** Client-side validation (HTML attributes) is a user convenience, not a security control. The server must always re-validate — a browser can be bypassed by sending an HTTP request directly.

---

## 6. Testing

### 6.1 Unit Tests

Unit tests verify individual functions in isolation, without running the full Flask server.

**What to unit test:**

- **Password hashing helper** — Confirm that hashing a plaintext password produces a hash, and that verifying the same plaintext against that hash returns true, while a different plaintext returns false.
- **Balance update logic** — If you extract the addition/subtraction logic into a pure function, test that depositing increases the value and withdrawing decreases it correctly.
- **Input parsing** — Test the function that parses a form amount string into a number. Confirm it handles valid numbers, empty strings, letters, and negative values as expected.

**How to structure unit tests:**

- Create a `tests/` folder at the project root.
- Write test functions using Python's built-in `unittest` module or the simpler `pytest` library (install via pip).
- Each test function should set up its own input, call the function under test, and assert the expected output. Tests should not depend on each other.

### 6.2 Integration Tests

Integration tests run the full Flask application with a test database and simulate real HTTP requests.

**What to integration test:**

- **Login flow** — Submit valid credentials, assert the response redirects to the dashboard. Submit invalid credentials, assert the login page is returned with an error message.
- **Session guard** — Make a GET request to `/dashboard` without logging in first, assert the response redirects to `/login`.
- **Deposit flow** — Log in, POST a valid deposit amount, assert the balance on the dashboard increases.
- **Withdraw flow** — Log in, POST a valid withdrawal, assert the balance decreases. Then POST an amount exceeding the balance, assert an error message appears and the balance is unchanged.
- **Logout flow** — Log in, then request `/logout`, assert the session is cleared and a subsequent visit to `/dashboard` redirects to login.

**How to structure integration tests:**

- Flask provides a built-in test client (`app.test_client()`) that lets you send requests without starting a real server.
- Use a separate in-memory SQLite database (or a temporary file) for tests so the real `banking.db` is never touched during test runs.
- Set Flask's `TESTING` configuration flag to `True` to disable error catching and make failures easier to debug.

### 6.3 Manual Testing Checklist

Use this checklist after each development phase and again before any deployment:

**Authentication**
- [ ] Visiting `/dashboard` without logging in redirects to `/login`
- [ ] Submitting the login form with an empty username shows an error
- [ ] Submitting the login form with an empty password shows an error
- [ ] Submitting correct credentials redirects to the dashboard
- [ ] Submitting wrong credentials shows a generic error and does not redirect
- [ ] Clicking Logout returns to the login page
- [ ] After logout, pressing the browser's Back button does not grant access to the dashboard

**Dashboard**
- [ ] Dashboard shows the correct customer name after login
- [ ] Dashboard shows the correct current balance
- [ ] Both deposit and withdraw forms are visible on the dashboard

**Deposit**
- [ ] Submitting a valid positive amount increases the balance correctly
- [ ] Submitting zero shows a validation error
- [ ] Submitting a negative number shows a validation error
- [ ] Submitting non-numeric text shows a validation error
- [ ] A success flash message appears after a successful deposit

**Withdraw**
- [ ] Submitting a valid amount less than the balance decreases the balance correctly
- [ ] Submitting an amount equal to the full balance reduces the balance to zero
- [ ] Submitting an amount greater than the balance shows "Insufficient funds" and does not change the balance
- [ ] Submitting zero or negative values shows a validation error
- [ ] A success flash message appears after a successful withdrawal

**General**
- [ ] All pages render correctly in Chrome and Firefox
- [ ] Flash messages appear and disappear correctly (do not persist across multiple page loads)
- [ ] No raw Python error messages or stack traces are visible to the user

---

## 7. Deployment

### 7.1 Run Locally

Follow these steps every time you want to run the application on your development machine:

1. Open a terminal and navigate to the project root directory.
2. Activate the virtual environment.
3. Navigate into the `BACKEND/` directory.
4. Set the `FLASK_APP` environment variable to `app.py` so Flask knows the entry point.
5. Optionally set `FLASK_ENV` to `development` to enable debug mode, which provides automatic code reloading and detailed error pages in the browser.
6. Run `flask run`.
7. Open a browser and visit `http://127.0.0.1:5000`.
8. Log in with the seeded test customer credentials.

To stop the server, press `Ctrl+C` in the terminal.

> **Note:** Debug mode must never be enabled in a production environment. It exposes an interactive Python debugger accessible from the browser, which is a critical security vulnerability.

### 7.2 Production Considerations

Flask's built-in development server is not suitable for serving real users. If this application were to move beyond a workshop environment, the following changes would be required:

| Concern | Development Approach | Production Requirement |
|---|---|---|
| **Web server** | Flask built-in (`flask run`) | A production WSGI server such as Gunicorn or Waitress |
| **Secret key** | Hardcoded string in `app.py` | A long random string stored in an environment variable, never in code |
| **Database** | Local SQLite file | A server-grade database (PostgreSQL, MySQL) for multi-user concurrency |
| **HTTPS** | Not used | TLS/SSL certificate required; a reverse proxy (nginx) handles termination |
| **Debug mode** | Enabled (`FLASK_ENV=development`) | Disabled entirely |
| **Password storage** | Werkzeug hash (already correct) | No change needed — bcrypt hashing is production-safe |
| **Static files** | Served by Flask | Served by the web server (nginx/Apache) or a CDN |
| **Environment config** | Values in code | All secrets and config in environment variables or a secrets manager |

For this workshop, these considerations are informational. The local development setup described in Section 7.1 is the intended deployment target.

---

*End of Step-by-Step Implementation Guide*
