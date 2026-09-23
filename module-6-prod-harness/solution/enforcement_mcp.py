"""
MCP Server for Enforcement Tools

This MCP server provides enforcement tools that can be used by
pre-built CLIs for security gates, linting, and validation.

Tools:
  - security_scan: Scan code for security issues
  - lint_code: Run linters on code
  - check_secrets: Check for potential secrets in files
  - validate_permissions: Validate permission boundaries

Usage with Claude Code:
  claude mcp add enforcement -- python3 /path/to/enforcement_mcp.py

Usage with OpenCode:
  Add to opencode.json under "mcp" configuration

Usage with Codex:
  Add to .codex/hooks.json under MCP servers
"""

import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any

# MCP server implementation using stdio transport

def send_response(response: dict):
    """Send a JSON-RPC response to stdout"""
    print(json.dumps(response), flush=True)
    print("---END---", flush=True)


def list_resources() -> list[dict]:
    """List MCP resources"""
    return []


def list_tools() -> list[dict]:
    """List MCP tools"""
    return [
        {
            "type": "function",
            "function": {
                "name": "security_scan",
                "description": "Scan code for security vulnerabilities including injection, XSS, hardcoded secrets",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the file to scan"
                        },
                        "content": {
                            "type": "string",
                            "description": "File content to scan (use instead of file_path)"
                        }
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "name": "lint_code",
            "description": "Run linter on code file or content",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to lint"
                    },
                    "content": {
                        "type": "string",
                        "description": "Code content to lint"
                    },
                    "language": {
                        "type": "string",
                        "description": "Language to lint (python, javascript, etc.)",
                        "default": "python"
                    }
                },
                "required": []
            }
        },
        {
            "type": "function",
            "name": "check_secrets",
            "description": "Check for potential secrets in files or content",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to check"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to check for secrets"
                    }
                },
                "required": []
            }
        },
        {
            "type": "function",
            "function": {
                "name": "validate_permissions",
                "description": "Validate that a code change respects permission boundaries",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "tool_calls": {
                            "type": "string",
                            "description": "JSON string of tool calls to validate"
                        },
                        "allowed_patterns": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of allowed tool call patterns"
                        }
                    },
                    "required": ["tool_calls"]
                }
            }
        }
    ]


def read_resource(uri: str) -> str:
    """Read a resource by URI"""
    return ""


def call_tool(name: str, arguments: dict) -> dict:
    """Execute a tool call"""
    if name == "security_scan":
        return security_scan(**arguments)
    elif name == "lint_code":
        return lint_code(**arguments)
    elif name == "check_secrets":
        return check_secrets(**arguments)
    elif name == "validate_permissions":
        return validate_permissions(**arguments)
    else:
        return {"error": f"Unknown tool: {name}"}


def security_scan(file_path: str = None, content: str = None) -> dict:
    """Scan code for security issues"""
    if content is None and file_path:
        with open(file_path) as f:
            content = f.read()

    if not content:
        return {"error": "No content to scan"}

    issues = []

    # Check for SQL injection
    sql_patterns = [
        r'execute\s*\(\s*f["\'].*\{.*\}.*["\']\s*\)',  # f-string SQL
        r'execute\s*\(\s*["\'].*\+.*["\']\s*\)',  # string concatenation SQL in execute
        r'cursor\.execute\s*\([^)]*\+',
        r'= "SELECT.*"\s*\+\s*',  # string concatenation building SQL query
        r'\+ str\(',  # string concatenation with str() for SQL
    ]
    for pattern in sql_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            issues.append({
                "type": "sql_injection_risk",
                "severity": "high",
                "message": "Potential SQL injection vulnerability detected",
                "pattern": pattern
            })

    # Check for hardcoded secrets
    secret_patterns = [
        (r'api[_-]?key\s*[:=]\s*["\']([a-zA-Z0-9_-]{16,})', "API key"),
        (r'secret\s*[:=]\s*["\']([a-zA-Z0-9_-]{16,})', "Secret"),
        (r'password\s*[:=]\s*["\']([a-zA-Z0-9_-]{8,})', "Password"),
        (r'token\s*[:=]\s*["\']([a-zA-Z0-9_-]{16,})', "Token"),
    ]
    for pattern, label in secret_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            issues.append({
                "type": "hardcoded_secret",
                "severity": "critical",
                "message": f"Potential hardcoded {label}: {match[:4]}...",
                "pattern": pattern
            })

    # Check for XSS
    xss_patterns = [
        r'dangerouslySetInnerHTML',
        r'\.innerHTML\s*=',
        r'document\.write\s*\(',
        r'f["\']<[^>]*>\{',  # f-string with HTML interpolation
    ]
    for pattern in xss_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            issues.append({
                "type": "xss_risk",
                "severity": "high",
                "message": "Potential XSS vulnerability detected",
                "pattern": pattern
            })

    # Check for command injection
    cmd_patterns = [
        r'subprocess\.(run|call|Popen)\s*\([^)]*shell\s*=\s*True',
        r'os\.system\s*\(',
        r'eval\s*\(',
    ]
    for pattern in cmd_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            issues.append({
                "type": "command_injection_risk",
                "severity": "medium",
                "message": "Potential command injection vulnerability",
                "pattern": pattern
            })

    return {
        "issues": issues,
        "total": len(issues),
        "high_severity": sum(1 for i in issues if i["severity"] in ("high", "critical")),
        "passed": len(issues) == 0
    }


def lint_code(file_path: str = None, content: str = None, language: str = "python") -> dict:
    """Run linter on code"""
    if content is None and file_path:
        with open(file_path) as f:
            content = f.read()

    if not content:
        return {"error": "No content to lint"}

    results = {"issues": [], "passed": True}

    if language == "python":
        # Check for missing type hints
        if re.search(r'def\s+\w+\s*\([^)]*\)\s*:', content):
            if not re.search(r'def\s+\w+\s*\([^)]*:\s', content):
                results["issues"].append({
                    "type": "missing_type_hints",
                    "severity": "medium",
                    "message": "Python functions should have type hints"
                })
                results["passed"] = False

        # Check for unused imports
        imports = re.findall(r'^import\s+(\w+)', content, re.MULTILINE)
        from_imports = re.findall(r'^from\s+\S+\s+import\s+(\w+)', content, re.MULTILINE)
        all_imports = imports + from_imports
        for imp in all_imports:
            if imp not in content.replace(f"import {imp}", "").replace(f"import {imp},", ""):
                results["issues"].append({
                    "type": "unused_import",
                    "severity": "low",
                    "message": f"Unused import: {imp}"
                })

    return results


def check_secrets(file_path: str = None, content: str = None) -> dict:
    """Check for secrets in code"""
    if content is None and file_path:
        with open(file_path) as f:
            content = f.read()

    if not content:
        return {"error": "No content to check"}

    found = []

    # Pattern matching for common secret formats
    patterns = {
        "aws_access_key": r'AKIA[0-9A-Z]{16}',
        "aws_secret": r'(?:aws_secret_access_key|secret_key)\s*[:=]\s*["\'][a-zA-Z0-9/+=]{40}["\']',
        "github_token": r'github_pat_[a-zA-Z0-9_]{82}',
        "private_key": r'-----BEGIN [A-Z ]+PRIVATE KEY-----',
        "generic_api_key": r'(?:api[_-]?key|apikey)\s*[:=]\s*["\']([a-zA-Z0-9_-]{20,})["\']',
        "password_literal": r'password\s*[:=]\s*["\'][^"\']{8,}["\']',
    }

    for name, pattern in patterns.items():
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            found.append({
                "type": name,
                "match": match[:10] + "..." if len(match) > 10 else match,
                "severity": "critical"
            })

    return {
        "found": found,
        "total": len(found),
        "passed": len(found) == 0
    }


def validate_permissions(tool_calls: str, allowed_patterns: list[str] = None) -> dict:
    """Validate that tool calls respect permission boundaries"""
    try:
        calls = json.loads(tool_calls) if isinstance(tool_calls, str) else tool_calls
    except json.JSONDecodeError:
        return {"error": "Invalid JSON in tool_calls"}

    allowed_patterns = allowed_patterns or []
    violations = []

    for call in calls:
        tool_name = call.get("tool", call.get("name", ""))
        tool_input = json.dumps(call.get("input", call.get("arguments", {})))

        # Check against allowed patterns
        is_allowed = False
        for pattern in allowed_patterns:
            if pattern == "*" or tool_name.startswith(pattern.replace("*", "")):
                is_allowed = True
                break

        if not is_allowed:
            violations.append({
                "tool": tool_name,
                "reason": "Tool not in allowed patterns"
            })

        # Check for dangerous commands
        dangerous = ["rm -rf", "git push.*--force", ":(){:|:&};", "shutdown", "reboot"]
        for danger in dangerous:
            if re.search(danger, tool_input, re.IGNORECASE):
                violations.append({
                    "tool": tool_name,
                    "reason": f"Dangerous command pattern detected: {danger}"
                })

    return {
        "valid": len(violations) == 0,
        "violations": violations,
        "total_calls": len(calls)
    }


# MCP Protocol Implementation

def handle_initialize(message_id: int, params: dict) -> dict:
    """Handle initialize request"""
    return {
        "jsonrpc": "2.0",
        "id": message_id,
        "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {},
                "resources": {},
                "prompts": {}
            },
            "serverInfo": {
                "name": "enforcement-mcp",
                "version": "1.0.0"
            }
        }
    }


def handle_tools_list(message_id: int) -> dict:
    """Handle tools/list request"""
    return {
        "jsonrpc": "2.0",
        "id": message_id,
        "result": {
            "tools": list_tools()
        }
    }


def handle_tools_call(message_id: int, params: dict) -> dict:
    """Handle tools/call request"""
    name = params.get("name", "")
    arguments = params.get("arguments", {})

    try:
        result = call_tool(name, arguments)
        return {
            "jsonrpc": "2.0",
            "id": message_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result, indent=2)
                    }
                ]
            }
        }
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": message_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps({"error": str(e)})
                    }
                ]
            }
        }


def main():
    """Main MCP server loop"""
    for line in os.fdopen(0, "r"):
        line = line.strip()
        if not line:
            continue

        try:
            message = json.loads(line)
            method = message.get("method", "")
            message_id = message.get("id")
            params = message.get("params", {})

            if method == "initialize":
                response = handle_initialize(message_id, params)
            elif method == "tools/list":
                response = handle_tools_list(message_id)
            elif method == "tools/call":
                response = handle_tools_call(message_id, params)
            elif method == "resources/list":
                response = {
                    "jsonrpc": "2.0",
                    "id": message_id,
                    "result": {"resources": list_resources()}
                }
            elif method == "resources/read":
                response = {
                    "jsonrpc": "2.0",
                    "id": message_id,
                    "result": {"contents": read_resource(params.get("uri", ""))}
                }
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": message_id,
                    "error": {"code": -32601, "message": f"Method not found: {method}"}
                }

            send_response(response)
        except json.JSONDecodeError:
            continue
        except Exception as e:
            send_response({
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32603, "message": str(e)}
            })


if __name__ == "__main__":
    main()
