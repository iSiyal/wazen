import sqlite3
import os

# Path to the sqlite database file at the workspace root
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "wazen.db"))

def get_connection():
    """
    Returns a sqlite3 connection to the database file.
    Enables foreign keys.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    """
    Initializes the SQLite database with transactions and monthly_budget tables.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create transactions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount REAL NOT NULL,
        category TEXT NOT NULL,
        type TEXT NOT NULL,
        timestamp TEXT NOT NULL
    );
    """)
    
    # Create monthly_budget table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS monthly_budget (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        month INTEGER NOT NULL,
        year INTEGER NOT NULL,
        "limit" REAL NOT NULL,
        currency TEXT DEFAULT 'SAR',
        UNIQUE(month, year)
    );
    """)
    
    conn.commit()
    conn.close()

# Automatically initialize database when db module is imported
init_db()
