# Banking Web Application — Implementation Plan

> **Status:** Planning  
> **Last Updated:** 2025  
> **Scope:** High-level architecture and phased roadmap only.  
> No database schema, SQL scripts, API contracts, or low-level code detail is included.

---

## 1. Solution Overview

### Objective

Build a lightweight, browser-based banking web application that allows customers to securely log in, view their account balance, deposit funds, withdraw funds, and log out — all served through a Python Flask backend and persisted in a local SQLite database.

### Scope

| In Scope | Out of Scope |
|---|---|
| Customer login / logout | Admin portal |
| Dashboard with account summary | Multi-user role management |
| View account balance | Inter-bank transfers |
| Deposit and withdraw funds | Email / SMS notifications |
| Session management | Payment gateway integration |
| Basic form validation (client + server) | Mobile native apps |

### Users

| User Type | Description |
|---|---|
| **Customer** | An authenticated bank customer who accesses their own account to view balance and perform transactions. |

### Functional Requirements

1. **FR-01 — Authentication:** A customer must be able to log in with a username and password, and log out to end their session.
2. **FR-02 — Dashboard:** After login, the customer is presented with a summary dashboard.
3. **FR-03 — View Balance:** The customer can view their current account balance at any time from the dashboard.
4. **FR-04 — Deposit Funds:** The customer can submit a deposit amount, which increases their balance.
5. **FR-05 — Withdraw Funds:** The customer can submit a withdrawal amount, which decreases their balance (subject to sufficient funds).
6. **FR-06 — Session Protection:** All dashboard and transaction pages are accessible only to authenticated customers.

### Non-Functional Requirements

| ID | Requirement |
|---|---|
| NFR-01 | The application must run entirely on a local machine with no external service dependencies. |
| NFR-02 | Pages must render correctly in modern desktop browsers. |
| NFR-03 | Bootstrap must be used for all UI layout and components. |
| NFR-04 | Backend and frontend must be clearly separated into their own top-level folders. |
| NFR-05 | Sensitive credentials must not be stored in plain text (passwords must be hashed). |

### Assumptions

- A single SQLite file is sufficient as the data store for this workshop context.
- Each customer has exactly one account.
- No concurrent multi-user scaling is required.
- Bootstrap is loaded via CDN (no local build step required for the frontend).
- Flask's built-in development server is the deployment target.

---

## 2. High-Level Architecture

### Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                        BROWSER                          │
│                                                         │
│   ┌───────────────────────────────────────────────┐    │
│   │            FRONTEND  (HTML + Bootstrap)        │    │
│   │   login.html  │  dashboard.html  │  forms      │    │
│   └───────────────┬───────────────────────────────┘    │
└───────────────────┼─────────────────────────────────────┘
                    │  HTTP Requests (form POST / GET)
                    ▼
┌─────────────────────────────────────────────────────────┐
│                  BACKEND  (Python Flask)                 │
│                                                         │
│   ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │
│   │  Auth Routes │  │  Dashboard   │  │ Transaction  │ │
│   │  /login      │  │  /dashboard  │  │  /deposit    │ │
│   │  /logout     │  │              │  │  /withdraw   │ │
│   └──────┬───────┘  └──────┬───────┘  └──────┬──────┘ │
│          └─────────────────┴──────────────────┘        │
│                             │                           │
│                      ┌──────▼──────┐                   │
│                      │  Data Layer │                   │
│                      │  (SQLite)   │                   │
│                      └─────────────┘                   │
└─────────────────────────────────────────────────────────┘
```

### Frontend → Backend → Database Interaction

| Layer | Technology | Responsibility |
|---|---|---|
| **Frontend** | HTML + Bootstrap | Renders UI, submits forms, displays server responses |
| **Backend** | Python Flask | Handles routing, session management, business logic, DB access |
| **Database** | SQLite | Persists customer credentials and account balances |

### Request Lifecycle

1. Customer enters credentials on the **Login page** and submits the form.
2. Flask's **Auth Route** validates credentials against the database.
3. On success, a **server-side session** is created and the customer is redirected to the Dashboard.
4. The **Dashboard Route** checks the session, queries the DB for the account balance, and renders the dashboard template.
5. Deposit/Withdraw form submissions are handled by **Transaction Routes**, which update the balance in the DB and redirect back to the Dashboard.
6. **Logout** clears the session and redirects to the Login page.
7. Any request to a protected route without a valid session is redirected to Login.

---

## 3. Component Design

### Frontend Responsibilities

- **Login Page** — Present a username/password form; display login errors returned by the backend.
- **Dashboard Page** — Show account holder name, current balance, and action buttons (Deposit / Withdraw / Logout).
- **Deposit Form** — Inline or modal form for submitting a deposit amount.
- **Withdraw Form** — Inline or modal form for submitting a withdrawal amount with client-side non-negative validation.
- **Flash Messages** — Display success or error messages returned from Flask using Bootstrap alerts.
- **Navigation / Layout** — Shared Bootstrap navbar and layout applied consistently across pages.
- All pages use Bootstrap classes for layout, typography, buttons, forms, and alerts.
- Templates are rendered server-side by Flask (Jinja2); the frontend has no independent JavaScript framework.

### Backend Responsibilities

- **Application Entry Point** — Initialises the Flask app, registers routes, configures the secret key, and starts the server.
- **Authentication Module** — Login form processing, password verification, session creation, and logout.
- **Dashboard Module** — Session guard, account data retrieval, and template rendering.
- **Transaction Module** — Deposit and withdrawal logic, balance updates, insufficient-funds guard, and redirect after processing.
- **Database Module** — Provides a single access point for DB connection and query execution; keeps SQL concerns isolated from route logic.
- **Session Management** — Flask's built-in server-side session (cookie-based) is used to track authenticated state.

### Database Responsibilities

- Persist **customer** records (identifier, hashed password, display name).
- Persist **account** records linked to each customer (current balance).
- The SQLite file lives inside the `BACKEND` folder and is excluded from version control.
- No direct SQL is executed from the frontend; all DB access goes through the backend data layer.

---

## 4. Folder Structure

```
banking-workshop_ibm/
│
├── FRONTEND/                        # All client-side assets
│   ├── templates/                   # Jinja2 HTML templates served by Flask
│   │   ├── login.html               # Login page
│   │   ├── dashboard.html           # Post-login dashboard
│   │   └── layout.html              # Base layout with Bootstrap CDN link
│   └── static/                      # Optional custom CSS / JS
│       └── style.css                # Project-specific overrides (if needed)
│
├── BACKEND/                         # Python Flask application
│   ├── app.py                       # App factory / entry point
│   ├── auth.py                      # Authentication routes and logic
│   ├── dashboard.py                 # Dashboard route and logic
│   ├── transactions.py              # Deposit / Withdraw routes and logic
│   ├── database.py                  # DB connection helper and query utilities
│   ├── banking.db                   # SQLite database file (git-ignored)
│   └── requirements.txt             # Python dependencies (flask, etc.)
│
├── docs/                            # Workshop and setup documentation
│   └── demo-setup/
│
├── IMPLEMENTATION_PLAN.md           # This document
└── README.md                        # Project overview and run instructions
```

### Folder Responsibilities

| Path | Responsibility |
|---|---|
| `FRONTEND/templates/` | Jinja2 HTML templates rendered by Flask; all UI lives here. |
| `FRONTEND/static/` | Static assets (custom CSS, any JS) that do not require server processing. |
| `BACKEND/app.py` | Creates and configures the Flask application; registers all blueprints/routes. |
| `BACKEND/auth.py` | Login, logout, and session handling logic. |
| `BACKEND/dashboard.py` | Protected dashboard route; fetches and displays account summary. |
| `BACKEND/transactions.py` | Deposit and withdrawal request handling and balance mutation. |
| `BACKEND/database.py` | Single point of contact for SQLite; opens connections, runs queries. |
| `BACKEND/banking.db` | Runtime SQLite file; created at first run, never committed to source control. |
| `BACKEND/requirements.txt` | Declares Python package dependencies for reproducible setup. |
| `docs/` | Workshop guides and CI/CD reference material; no application code. |

---

## 5. Module Breakdown

### 5.1 Authentication Module

**Goal:** Verify customer identity and manage session lifecycle.

| Concern | Detail |
|---|---|
| Login | Accept POST form, look up customer by username, verify hashed password, create session on success. |
| Session guard | Decorator or helper applied to all protected routes to redirect unauthenticated requests to Login. |
| Logout | Clear the server-side session and redirect to Login. |
| Error feedback | Return descriptive flash messages for invalid credentials (without revealing which field was wrong). |

### 5.2 Dashboard Module

**Goal:** Provide the authenticated customer with a personalised account overview.

| Concern | Detail |
|---|---|
| Route protection | Verify session before rendering; redirect to Login if not authenticated. |
| Data retrieval | Query the DB for the customer's display name and current balance. |
| Template rendering | Pass balance and customer name to `dashboard.html`; display any pending flash messages. |

### 5.3 Account Management Module

**Goal:** Expose the customer's balance as a readable value sourced from the database.

| Concern | Detail |
|---|---|
| Balance read | Fetch the current balance for the session's customer from the database. |
| Data ownership | Each customer owns exactly one account; queries are always scoped by customer identity from the session. |

### 5.4 Transaction Module

**Goal:** Handle deposit and withdrawal requests and update the persisted balance.

| Concern | Detail |
|---|---|
| Deposit | Accept a positive amount, add to balance, persist, flash success, redirect to Dashboard. |
| Withdrawal | Accept a positive amount, verify sufficient balance, subtract, persist, flash success or error, redirect. |
| Validation | Reject non-positive amounts and non-numeric input at the route level before touching the DB. |
| Atomicity | Each transaction is a single DB write; no partial updates. |

---

## 6. Implementation Roadmap

### Development Phases

#### Phase 1 — Project Scaffolding
**Goal:** Establish the folder structure, Flask app skeleton, and verify the development environment is runnable.

| Task | Dependency |
|---|---|
| Create `FRONTEND/` and `BACKEND/` directory trees | None |
| Create `BACKEND/requirements.txt` with Flask listed | None |
| Create `BACKEND/app.py` as a minimal Flask app that returns a placeholder page | requirements.txt |
| Create `FRONTEND/templates/layout.html` with Bootstrap CDN | app.py renders templates |
| Confirm `flask run` starts without errors | All above |

**Effort:** Small  
**Exit Criteria:** `flask run` starts, browser shows placeholder page with Bootstrap loaded.

---

#### Phase 2 — Database Layer
**Goal:** Establish the SQLite database and the data access helper module.

| Task | Dependency |
|---|---|
| Create `BACKEND/database.py` with connection helper | Phase 1 complete |
| Define and initialise the customer and account tables at app startup | database.py |
| Seed at least one test customer with a hashed password | Table initialisation |

**Effort:** Small  
**Exit Criteria:** `banking.db` is created on first run and contains seeded data.

---

#### Phase 3 — Authentication
**Goal:** Implement login/logout and session management.

| Task | Dependency |
|---|---|
| Create `BACKEND/auth.py` with `/login` (GET + POST) and `/logout` routes | Phase 2 complete |
| Create `FRONTEND/templates/login.html` with Bootstrap form | auth.py routes |
| Implement session guard helper for use in protected routes | auth.py |
| Flash error messages on invalid login | login.html displays alerts |

**Effort:** Medium  
**Exit Criteria:** A seeded customer can log in, is redirected to a placeholder dashboard, and logout clears the session.

---

#### Phase 4 — Dashboard
**Goal:** Render the authenticated dashboard with account summary.

| Task | Dependency |
|---|---|
| Create `BACKEND/dashboard.py` with `/dashboard` route (session-guarded) | Phase 3 complete |
| Create `FRONTEND/templates/dashboard.html` with balance display and action buttons | dashboard.py |
| Fetch and display customer name and balance from DB | database.py |

**Effort:** Small  
**Exit Criteria:** Logged-in customer sees their name and current balance on the dashboard.

---

#### Phase 5 — Transactions
**Goal:** Implement deposit and withdrawal features.

| Task | Dependency |
|---|---|
| Create `BACKEND/transactions.py` with `/deposit` and `/withdraw` routes | Phase 4 complete |
| Handle deposit: validate amount, update balance, flash success | database.py write |
| Handle withdrawal: validate amount, check balance, update, flash success or error | database.py write |
| Update `dashboard.html` to include deposit and withdraw forms/buttons | transactions.py routes |

**Effort:** Medium  
**Exit Criteria:** Customer can deposit and withdraw; balance updates correctly; error shown for overdraft.

---

#### Phase 6 — Polish and Validation
**Goal:** Ensure UI consistency, session security, and basic input validation are all in place.

| Task | Dependency |
|---|---|
| Apply Bootstrap alerts for all flash messages across templates | All routes complete |
| Add client-side input validation (non-empty, positive number) to forms | dashboard.html |
| Confirm all routes redirect to login when session is missing | Session guard |
| Review and update `README.md` with run instructions | All above |

**Effort:** Small  
**Exit Criteria:** All features work end-to-end; no unguarded routes; README is accurate.

---

### Dependency Summary

```
Phase 1 (Scaffolding)
    └── Phase 2 (Database Layer)
            └── Phase 3 (Authentication)
                    └── Phase 4 (Dashboard)
                            └── Phase 5 (Transactions)
                                    └── Phase 6 (Polish)
```

### Effort Legend

| Label | Meaning |
|---|---|
| Small | Focused, few files touched, low risk |
| Medium | Multiple files, some logic complexity |
| Large | Cross-cutting concern, higher coordination need |

---

*End of Implementation Plan*
