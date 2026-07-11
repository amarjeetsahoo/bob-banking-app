import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "banking.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS customers (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT    NOT NULL UNIQUE,
            password_hash TEXT    NOT NULL,
            display_name  TEXT    NOT NULL
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS accounts (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL REFERENCES customers(id),
            balance     REAL    NOT NULL DEFAULT 0.0
        )
        """
    )

    row = conn.execute("SELECT 1 FROM customers LIMIT 1").fetchone()
    if row is None:
        cursor = conn.execute(
            """
            INSERT INTO customers (username, password_hash, display_name)
            VALUES (?, ?, ?)
            """,
            ("testuser", generate_password_hash("password123"), "Test User"),
        )
        customer_id = cursor.lastrowid

        conn.execute(
            """
            INSERT INTO accounts (customer_id, balance)
            VALUES (?, ?)
            """,
            (customer_id, 1000.00),
        )

    conn.commit()
    conn.close()


def get_customer_by_username(username):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM customers WHERE username = ?",
        (username,),
    ).fetchone()
    conn.close()
    return row


def get_account_by_customer_id(customer_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM accounts WHERE customer_id = ?",
        (customer_id,),
    ).fetchone()
    conn.close()
    return row


def update_balance(customer_id, new_balance):
    conn = get_connection()
    conn.execute(
        "UPDATE accounts SET balance = ? WHERE customer_id = ?",
        (new_balance, customer_id),
    )
    conn.commit()
    conn.close()
