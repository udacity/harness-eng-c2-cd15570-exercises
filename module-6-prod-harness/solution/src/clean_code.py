"""
Example module with clean, secure code for testing evaluation systems.

This file should pass all enforcement checks.
"""

import sqlite3
from typing import Optional, List, Dict, Any


class SafeAuthenticator:
    """Secure authentication handler."""

    def __init__(self, database_url: str):
        self.db_url = database_url

    def authenticate_user(self, username: str, password: str) -> bool:
        """Authenticate a user against the database.

        Args:
            username: The username to authenticate
            password: The password hash to verify

        Returns:
            True if authentication succeeds, False otherwise
        """
        if not username or not password:
            return False

        conn = sqlite3.connect(self.db_url)
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT password_hash FROM users WHERE username = ?",
                (username,)
            )
            result = cursor.fetchone()
            if result is None:
                return False
            return self._verify_password(password, result[0])
        finally:
            conn.close()

    def _verify_password(self, password: str, stored_hash: str) -> bool:
        """Verify password against stored hash."""
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest() == stored_hash


def get_user_data(user_id: int) -> Optional[Dict[str, Any]]:
    """Safely retrieve user data using parameterized queries.

    Args:
        user_id: The numeric user ID

    Returns:
        User data dict or None if not found
    """
    if not isinstance(user_id, int) or user_id < 0:
        raise ValueError("user_id must be a non-negative integer")

    conn = sqlite3.connect("app.db")
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, email FROM users WHERE id = ?",
            (user_id,)
        )
        result = cursor.fetchone()
        if result:
            return {"id": result[0], "username": result[1], "email": result[2]}
        return None
    finally:
        conn.close()


def calculate_total(items: List[Dict[str, float]], tax_rate: float) -> float:
    """Calculate total price including tax.

    Args:
        items: List of items with 'price' key
        tax_rate: Tax rate as decimal (e.g., 0.08 for 8%)

    Returns:
        Total amount including tax
    """
    if tax_rate < 0:
        raise ValueError("Tax rate cannot be negative")

    subtotal = sum(item.get("price", 0) for item in items)
    return subtotal * (1 + tax_rate)
