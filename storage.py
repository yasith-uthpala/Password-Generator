"""
storage.py - SQLite database layer for storing encrypted passwords.

Improvements applied:
  ✅ SQLite instead of plain text file
  ✅ Full CRUD support (add, view, search, edit, delete)
"""

import sqlite3
import os

DB_FILE = "vault.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_db():
    """Create the passwords table if it doesn't exist."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS passwords (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                site      TEXT NOT NULL,
                username  TEXT NOT NULL,
                password  TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


def insert_password(site: str, username: str, password: str):
    """Insert a new encrypted record."""
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO passwords (site, username, password) VALUES (?, ?, ?)",
            (site, username, password)
        )
        conn.commit()


def get_all_passwords() -> list:
    """Return all records."""
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM passwords ORDER BY site"
        ).fetchall()


def get_password_by_id(entry_id: int):
    """Fetch a single record by ID."""
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM passwords WHERE id = ?", (entry_id,)
        ).fetchone()


def update_password(entry_id: int, site: str, username: str, password: str):
    """Update an existing record."""
    with get_connection() as conn:
        conn.execute(
            """UPDATE passwords
               SET site = ?, username = ?, password = ?, updated_at = CURRENT_TIMESTAMP
               WHERE id = ?""",
            (site, username, password, entry_id)
        )
        conn.commit()


def delete_password_by_id(entry_id: int):
    """Delete a record by ID."""
    with get_connection() as conn:
        conn.execute("DELETE FROM passwords WHERE id = ?", (entry_id,))
        conn.commit()


# Initialize DB on import
initialize_db()