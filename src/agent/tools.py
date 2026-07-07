import sqlite3
from datetime import datetime, timedelta
from agent.db import get_connection

def log_transaction_tool(amount: float, category: str, transaction_type: str) -> str:
    """
    Inserts a new row into the transactions table.
    Automatically injects the current timestamp using datetime.
    Returns a success or error message string.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Automatically injects current timestamp in ISO 8601 format
        timestamp = datetime.now().isoformat()
        
        cursor.execute(
            "INSERT INTO transactions (amount, category, type, timestamp) VALUES (?, ?, ?, ?)",
            (amount, category, transaction_type, timestamp)
        )
        conn.commit()
        conn.close()
        return f"Success: Transaction of {amount} ({transaction_type}) logged under category '{category}'."
    except Exception as e:
        return f"Error logging transaction: {str(e)}"

def get_budget_summary_tool(month: int = 7, year: int = 2026) -> dict:
    """
    Fetches the total limit from the monthly_budget table for the specified month/year.
    Sums up all expenses (type='expense') from the transactions table for that same month/year.
    Returns a dict containing: total_budget, total_spent, remaining_budget, and currency.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # 1. Fetch the total budget limit and currency from monthly_budget
        cursor.execute(
            'SELECT SUM("limit"), currency FROM monthly_budget WHERE month = ? AND year = ?',
            (month, year)
        )
        row = cursor.fetchone()
        
        total_budget = float(row[0]) if (row and row[0] is not None) else 0.0
        currency = row[1] if (row and row[1] is not None) else "SAR"
        
        # 2. Sum up all expenses for that month/year from transactions table
        cursor.execute(
            """
            SELECT SUM(amount) 
            FROM transactions 
            WHERE type = 'expense' 
              AND CAST(strftime('%m', timestamp) AS INTEGER) = ? 
              AND CAST(strftime('%Y', timestamp) AS INTEGER) = ?
            """,
            (month, year)
        )
        row_spent = cursor.fetchone()
        total_spent = float(row_spent[0]) if (row_spent and row_spent[0] is not None) else 0.0
        
        conn.close()
        
        remaining_budget = total_budget - total_spent
        
        return {
            "total_budget": total_budget,
            "total_spent": total_spent,
            "remaining_budget": remaining_budget,
            "currency": currency
        }
    except Exception as e:
        return {
            "total_budget": 0.0,
            "total_spent": 0.0,
            "remaining_budget": 0.0,
            "currency": "SAR",
            "error": str(e)
        }

def get_category_spending_tool(days_back: int = 30) -> dict:
    """
    Queries the transactions table to sum up spending grouped by category (category) over the trailing X days.
    Returns a clean key-value dictionary where the key is the category name string and the value is the calculated float sum.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Calculate threshold timestamp in Python for timezone-safety and consistency
        threshold_date = datetime.now() - timedelta(days=days_back)
        threshold_str = threshold_date.isoformat()
        
        # Sum spending (type = 'expense') grouped by category over the trailing X days
        cursor.execute(
            """
            SELECT category, SUM(amount) 
            FROM transactions 
            WHERE type = 'expense' AND timestamp >= ? 
            GROUP BY category
            """,
            (threshold_str,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        return {str(row[0]): float(row[1]) for row in rows if row[0] is not None and row[1] is not None}
    except Exception as e:
        return {}
