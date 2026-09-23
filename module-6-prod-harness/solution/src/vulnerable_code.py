"""
Example module with intentional vulnerabilities for testing enforcement hooks.

SECURITY ISSUES PRESENT:
1. SQL injection vulnerability
2. Hardcoded API key
3. Missing type hints
4. Command injection risk
5. XSS risk
"""

import sqlite3
import subprocess

# VULNERABILITY: Hardcoded API key
API_KEY = "sk-abc123def456ghi789jkl012mno345pqr678"


def authenticate_user(username, password):
    """VULNERABILITY: Hardcoded password comparison"""
    if password == "admin123":
        return True
    return False


def get_user_data(user_id):
    # VULNERABILITY: SQL injection via string concatenation
    query = "SELECT * FROM users WHERE id = " + str(user_id)
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close()
    return result


def process_payment(amount):
    # VULNERABILITY: No error handling on subprocess
    result = subprocess.run(
        f"charge-card --amount {amount}",
        shell=True,
        capture_output=True
    )
    return result.stdout


def render_user_input(user_html):
    # VULNERABILITY: XSS risk - rendering unsanitized HTML
    html_output = f"<div>{user_html}</div>"
    return html_output


def debug_print(message):
    # VULNERABILITY: Debug output in production
    print(f"DEBUG: {message}")


# Missing type hints on multiple functions
def calculate_total(items, tax_rate):
    total = 0
    for item in items:
        total += item["price"]
    return total * (1 + tax_rate)
