"""
Database module for SPEED MOI.
Manages the SQLite database speed_moi.db, table creation, foreign keys, and queries.
"""

import sqlite3
import os

def get_db_file():
    return os.environ.get('SPEED_MOI_DB') or os.path.join(os.path.dirname(os.path.abspath(__file__)), 'speed_moi.db')

def get_db():
    """
    Connect to the SQLite database and return a connection with row factory.
    Enforces SQLite foreign keys.
    """
    conn = sqlite3.connect(get_db_file())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    """
    Initializes the database and creates tables if they do not exist:
      - users (admin credentials)
      - functions (events/weddings/moi functions)
      - contributions (individual moi entries)
    """
    conn = get_db()
    with conn:
        # Table 1: users
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Table 2: functions
        conn.execute("""
            CREATE TABLE IF NOT EXISTS functions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                function_name TEXT NOT NULL,
                coordinator_name TEXT NOT NULL,
                function_date TEXT NOT NULL,
                host_details TEXT DEFAULT '',
                venue TEXT DEFAULT '',
                contact_number TEXT DEFAULT '',
                clerk_name TEXT DEFAULT '',
                next_bill_number INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Table 3: contributions
        conn.execute("""
            CREATE TABLE IF NOT EXISTS contributions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                function_id INTEGER NOT NULL REFERENCES functions(id) ON DELETE CASCADE,
                bill_number INTEGER NOT NULL,
                contributor_name TEXT NOT NULL,
                native_place TEXT NOT NULL,
                amount INTEGER NOT NULL,
                entry_date TEXT NOT NULL,
                entry_time TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
    conn.close()

def has_any_user():
    """Checks if at least one user exists in the database."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM users")
    row = cursor.fetchone()
    count = row['count'] if row else 0
    conn.close()
    return count > 0

def get_user_by_username(username):
    """Fetches a user record by username."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username.strip(),))
    user = cursor.fetchone()
    conn.close()
    return user

def create_user(username, password_hash):
    """Inserts a new user."""
    conn = get_db()
    try:
        with conn:
            cursor = conn.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username.strip(), password_hash)
            )
            return cursor.lastrowid
    finally:
        conn.close()

def update_user_password(username, new_password_hash):
    """Updates password hash for a given user."""
    conn = get_db()
    with conn:
        cursor = conn.execute(
            "UPDATE users SET password_hash = ? WHERE username = ?",
            (new_password_hash, username.strip())
        )
        updated = cursor.rowcount > 0
    conn.close()
    return updated

def create_function(function_name, coordinator_name, function_date, host_details='', venue='', contact_number='', clerk_name=''):
    """Creates a new function record with optional bill details and returns its ID."""
    conn = get_db()
    # If clerk_name is empty, default to coordinator_name
    clerk = clerk_name.strip() if clerk_name and clerk_name.strip() else coordinator_name.strip()
    with conn:
        cursor = conn.execute(
            """
            INSERT INTO functions (
                function_name, coordinator_name, function_date,
                host_details, venue, contact_number, clerk_name, next_bill_number
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, 1)
            """,
            (
                function_name.strip(),
                coordinator_name.strip(),
                function_date.strip(),
                host_details.strip() if host_details else '',
                venue.strip() if venue else '',
                contact_number.strip() if contact_number else '',
                clerk
            )
        )
        new_id = cursor.lastrowid
    conn.close()
    return new_id

def get_function(function_id):
    """Retrieves a function by ID."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM functions WHERE id = ?", (function_id,))
    func = cursor.fetchone()
    conn.close()
    return func

def get_all_functions():
    """Retrieves all functions ordered by creation date descending."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT f.*, 
               (SELECT COUNT(*) FROM contributions c WHERE c.function_id = f.id) as total_contributors,
               (SELECT COALESCE(SUM(amount), 0) FROM contributions c WHERE c.function_id = f.id) as total_amount
        FROM functions f
        ORDER BY f.id DESC
    """)
    functions = cursor.fetchall()
    conn.close()
    return functions

def save_contribution(function_id, contributor_name, native_place, amount, entry_date, entry_time):
    """
    Atomically generates the next bill number for the function,
    increments the function's counter, and stores the contribution.
    Returns (new_contribution_id, bill_number_int).
    """
    conn = get_db()
    with conn:
        cursor = conn.cursor()
        # Fetch current next_bill_number
        cursor.execute("SELECT next_bill_number FROM functions WHERE id = ?", (function_id,))
        func_row = cursor.fetchone()
        if not func_row:
            conn.close()
            raise ValueError(f"Function ID {function_id} does not exist.")

        bill_num = func_row['next_bill_number']

        # Increment next_bill_number in functions table
        cursor.execute(
            "UPDATE functions SET next_bill_number = next_bill_number + 1 WHERE id = ?",
            (function_id,)
        )

        # Insert new contribution
        cursor.execute(
            """
            INSERT INTO contributions (
                function_id, bill_number, contributor_name,
                native_place, amount, entry_date, entry_time
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                function_id,
                bill_num,
                contributor_name.strip(),
                native_place.strip(),
                int(amount),
                entry_date.strip(),
                entry_time.strip()
            )
        )
        contrib_id = cursor.lastrowid

    conn.close()
    return contrib_id, bill_num

def get_contribution(contribution_id):
    """Retrieves a single contribution record with associated function details."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.*, 
               f.function_name, 
               f.coordinator_name, 
               f.function_date,
               f.host_details,
               f.venue,
               f.contact_number,
               f.clerk_name
        FROM contributions c
        JOIN functions f ON c.function_id = f.id
        WHERE c.id = ?
    """, (contribution_id,))
    row = cursor.fetchone()
    conn.close()
    return row

def get_recent_contributions(function_id, limit=5):
    """Fetches the most recently recorded contributions for a function."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM contributions 
        WHERE function_id = ? 
        ORDER BY id DESC 
        LIMIT ?
    """, (function_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return rows

