# SecureBank — Banking Web Application

A lightweight, full-stack banking application built with **Python Flask**, **Bootstrap 5**, and **SQLite**.

---

## Features

| Feature | Description |
|---|---|
| Customer Login | Secure login with hashed password verification |
| Dashboard | Personalised account overview with live balance |
| View Balance | Current balance displayed prominently on the dashboard |
| Deposit Funds | Add money to the account with instant balance update |
| Withdraw Funds | Withdraw money with insufficient-funds protection |
| Logout | Clears the session and redirects to the login page |

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | HTML5 + Bootstrap 5.3 (Jinja2 templates) |
| **Backend** | Python 3.9+ · Flask 3.0 |
| **Database** | SQLite (via Python's built-in `sqlite3`) |
| **Auth** | Werkzeug password hashing (bcrypt-compatible) |

---

## Project Structure

```
banking-workshop_ibm/
├── FRONTEND/
│   ├── templates/
│   │   ├── layout.html        # Base template — navbar, flash messages, Bootstrap CDN
│   │   ├── login.html         # Login page
│   │   └── dashboard.html     # Authenticated dashboard with deposit/withdraw forms
│   └── static/
│       └── style.css          # Project-specific CSS overrides
│
├── BACKEND/
│   ├── app.py                 # Flask entry point — wires everything together
│   ├── auth.py                # Login, logout, login_required decorator
│   ├── dashboard.py           # Dashboard route
│   ├── transactions.py        # Deposit and withdraw routes + parse_amount helper
│   ├── database.py            # SQLite data access layer (all SQL lives here)
│   └── requirements.txt       # Python dependencies
│
├── tests/
│   ├── test_unit.py           # 17 unit tests — hashing, parsing, arithmetic
│   └── test_integration.py    # 14 integration tests — full request/response flows
│
├── .gitignore
├── IMPLEMENTATION_PLAN.md
├── STEP_BY_STEP_IMPLEMENTATION_GUIDE.md
└── README.md
```

---

## Prerequisites

- **Python 3.9 or later** — check with `python --version`
- **pip** — bundled with Python

---

## Setup & Run

### 1 — Clone / open the project

```bash
cd banking-workshop_ibm
```

### 2 — Create and activate a virtual environment

```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3 — Install dependencies

```bash
pip install -r BACKEND/requirements.txt
```

### 4 — Start the application

```bash
cd BACKEND
flask --app app run --debug
```

Open your browser and visit **http://127.0.0.1:5000**

Press `Ctrl+C` in the terminal to stop the server.

---

## Default Login Credentials

| Field | Value |
|---|---|
| **Username** | `testuser` |
| **Password** | `password123` |
| **Starting balance** | $1,000.00 |

> These credentials are seeded automatically the first time the app starts.

---

## Run Tests

From the **project root** (not BACKEND/):

```bash
pytest tests/ -v
```

Expected output: **31 passed**

| Suite | Tests | Coverage |
|---|---|---|
| `test_unit.py` | 17 | Password hashing, amount parsing, balance arithmetic |
| `test_integration.py` | 14 | Login, logout, session guard, deposit, withdraw, overdraft |

---

## Application Flow

```
Browser
  │
  ├─ GET  /           → redirects to /login
  ├─ GET  /login      → shows login form
  ├─ POST /login      → validates credentials → sets session → /dashboard
  │
  ├─ GET  /dashboard  → [login required] shows balance + forms
  ├─ POST /deposit    → [login required] validates → updates balance → /dashboard
  ├─ POST /withdraw   → [login required] validates → checks funds → updates → /dashboard
  │
  └─ GET  /logout     → clears session → /login
```

---

## Security Notes

| Concern | Approach |
|---|---|
| Passwords | Stored as Werkzeug bcrypt-compatible hashes — never plaintext |
| Session | Flask signed cookie using `secret_key` — tamper-proof |
| SQL injection | All queries use parameterised `?` placeholders |
| Auth bypass | `login_required` decorator protects all sensitive routes |
| Error messages | Generic "Invalid username or password" — does not reveal which field failed |

> **Note:** The `secret_key` in `app.py` is a development placeholder. In production, replace it with a long random string stored in an environment variable.

---

## Production Checklist

- [ ] Replace `app.secret_key` with a value from an environment variable
- [ ] Disable `debug=True` — never expose the debugger in production
- [ ] Serve with a WSGI server (Gunicorn, Waitress) instead of Flask's dev server
- [ ] Migrate to PostgreSQL or MySQL for multi-user concurrency
- [ ] Add HTTPS via a reverse proxy (nginx + Let's Encrypt)
