from fastmcp import FastMCP
import json
import os
import random
import sqlite3
from typing import Any, Dict, List, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "expenses.db")

mcp = FastMCP("Simple testing of FastMCP", "This is a simple test of the FastMCP library.")


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_db_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            description TEXT NOT NULL,
            category TEXT DEFAULT 'general',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


init_db()


@mcp.tool
def random_number_generator():
    """Generates a random number between 1 and 100.

    args:
        None

    returns:
        int: A random integer between 1 and 100.
    """
    return random.randint(1, 100)


@mcp.tool
def add_numbers(a: int, b: int) -> int:
    """Adds two numbers and returns the result.

    args:
        a (int): The first number to add.
        b (int): The second number to add.
    returns:
        int: The sum of the two numbers.
    """
    return a + b


@mcp.tool
def multiply_numbers(a: int, b: int) -> int:
    """Multiplies two numbers and returns the result.

    args:
        a (int): The first number to multiply.
        b (int): The second number to multiply.
    returns:
        int: The product of the two numbers.
    """
    return a * b


@mcp.tool
def add_expense(amount: float, description: str, category: str = "general") -> Dict[str, Any]:
    """Adds an expense record to the SQLite database.

    args:
        amount (float): Expense amount.
        description (str): Brief description of the expense.
        category (str): Optional expense category. Defaults to "general".

    returns:
        dict: The inserted expense data.
    """
    conn = get_db_connection()
    cursor = conn.execute(
        "INSERT INTO expenses (amount, description, category) VALUES (?, ?, ?)",
        (amount, description, category),
    )
    conn.commit()
    expense_id = cursor.lastrowid
    expense = conn.execute(
        "SELECT id, amount, description, category, created_at FROM expenses WHERE id = ?",
        (expense_id,),
    ).fetchone()
    conn.close()
    return dict(expense) if expense else {"id": expense_id, "amount": amount, "description": description, "category": category}


@mcp.tool
def list_expenses() -> List[Dict[str, Any]]:
    """Returns all expenses from the SQLite database.

    returns:
        list: A list of all expense records.
    """
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT id, amount, description, category, created_at FROM expenses ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


@mcp.tool
def get_expense(expense_id: int) -> Optional[Dict[str, Any]]:
    """Fetches one expense by its ID.

    args:
        expense_id (int): The ID of the expense to fetch.

    returns:
        dict | None: The matching expense or None if it does not exist.
    """
    conn = get_db_connection()
    row = conn.execute(
        "SELECT id, amount, description, category, created_at FROM expenses WHERE id = ?",
        (expense_id,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


@mcp.tool
def total_expenses() -> float:
    """Returns the total of all recorded expenses.

    returns:
        float: Total amount spent.
    """
    conn = get_db_connection()
    result = conn.execute("SELECT COALESCE(SUM(amount), 0) as total FROM expenses").fetchone()
    conn.close()
    return float(result["total"]) if result and result["total"] is not None else 0.0


@mcp.tool
def delete_expense(expense_id: int) -> Dict[str, Any]:
    """Deletes an expense from the database by ID.

    args:
        expense_id (int): The expense ID to delete.

    returns:
        dict: Confirmation payload with the deleted ID.
    """
    conn = get_db_connection()
    existing = conn.execute("SELECT id FROM expenses WHERE id = ?", (expense_id,)).fetchone()
    if existing is None:
        conn.close()
        return {"success": False, "message": f"Expense with id {expense_id} not found."}

    conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()
    return {"success": True, "deleted_id": expense_id}


@mcp.resource("info://server")
def server_info():
    """Returns information about the server."""
    info = {
        "server_name": "FastMCP Test Server",
        "version": "1.0.0",
        "description": "This server is used for testing the FastMCP library.",
        "tools": [
            "random_number_generator",
            "add_numbers",
            "multiply_numbers",
            "add_expense",
            "list_expenses",
            "get_expense",
            "total_expenses",
            "delete_expense",
        ],
        "authors": ["Vivek Singh"],
    }

    return json.dumps(info, indent=4)


if __name__ == "__main__":
    mcp.run(transport="http", host="localhost", port=8000)