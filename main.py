from fastmcp import FastMCP

import json
import os
import random
from typing import Any, Dict, List, Optional

from supabase import Client, create_client


# ============================================================
# Supabase configuration
# ============================================================

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL:
    raise RuntimeError("SUPABASE_URL environment variable is not set")

if not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_KEY environment variable is not set")


supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY,
)


# ============================================================
# FastMCP server
# ============================================================

mcp = FastMCP(
    "Simple testing of FastMCP",
    "This is a simple test of the FastMCP library.",
)


# ============================================================
# Basic test tools
# ============================================================

@mcp.tool
def random_number_generator() -> int:
    """Generates a random number between 1 and 100."""
    return random.randint(1, 100)


@mcp.tool
def add_numbers(a: int, b: int) -> int:
    """Adds two numbers and returns the result."""
    return a + b


@mcp.tool
def multiply_numbers(a: int, b: int) -> int:
    """Multiplies two numbers and returns the result."""
    return a * b


# ============================================================
# Expense tools
# ============================================================

@mcp.tool
def add_expense(
    amount: float,
    description: str,
    category: str = "general",
) -> Dict[str, Any]:
    """
    Adds an expense record to Supabase.

    Args:
        amount: Expense amount.
        description: Brief description of the expense.
        category: Expense category. Defaults to "general".

    Returns:
        The inserted expense record.
    """

    response = (
        supabase
        .table("expenses")
        .insert({
            "amount": amount,
            "description": description,
            "category": category,
        })
        .execute()
    )

    if not response.data:
        return {
            "success": False,
            "message": "Expense could not be created.",
        }

    return {
        "success": True,
        "expense": response.data[0],
    }


@mcp.tool
def list_expenses() -> List[Dict[str, Any]]:
    """
    Returns all expenses from Supabase.

    Returns:
        List of expense records.
    """

    response = (
        supabase
        .table("expenses")
        .select("id, amount, description, category, created_at")
        .order("created_at", desc=True)
        .execute()
    )

    return response.data or []


@mcp.tool
def get_expense(
    expense_id: int,
) -> Optional[Dict[str, Any]]:
    """
    Fetches one expense by ID.

    Args:
        expense_id: The ID of the expense to fetch.

    Returns:
        The matching expense or None.
    """

    response = (
        supabase
        .table("expenses")
        .select("id, amount, description, category, created_at")
        .eq("id", expense_id)
        .execute()
    )

    if not response.data:
        return None

    return response.data[0]


@mcp.tool
def total_expenses() -> float:
    """
    Returns the total of all recorded expenses.

    Returns:
        Total amount spent.
    """

    response = (
        supabase
        .table("expenses")
        .select("amount")
        .execute()
    )

    if not response.data:
        return 0.0

    total = sum(
        float(row["amount"])
        for row in response.data
        if row.get("amount") is not None
    )

    return total


@mcp.tool
def delete_expense(
    expense_id: int,
) -> Dict[str, Any]:
    """
    Deletes an expense by ID.

    Args:
        expense_id: The expense ID to delete.

    Returns:
        Confirmation payload.
    """

    # First check whether the expense exists
    existing = (
        supabase
        .table("expenses")
        .select("id")
        .eq("id", expense_id)
        .execute()
    )

    if not existing.data:
        return {
            "success": False,
            "message": f"Expense with id {expense_id} not found.",
        }

    # Delete
    (
        supabase
        .table("expenses")
        .delete()
        .eq("id", expense_id)
        .execute()
    )

    return {
        "success": True,
        "deleted_id": expense_id,
    }


# ============================================================
# Server resource
# ============================================================

@mcp.resource("info://server")
def server_info() -> str:
    """Returns information about the server."""

    info = {
        "server_name": "FastMCP Test Server",
        "version": "2.0.0",
        "description": "FastMCP server using Supabase PostgreSQL.",
        "database": "Supabase PostgreSQL",
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


# ============================================================
# Local development
# ============================================================

if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="localhost",
        port=8000,
    )