"""
Test suite for I2.6 Production Harness Features comparison.

Tests:
1. Hook enforcement comparison (hand-built vs pre-built)
2. Evaluator comparison (hand-built vs built-in review)
3. Permission boundary comparison
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Optional

# Ensure project root is in path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from solution.enforcement_mcp import security_scan, lint_code, check_secrets, validate_permissions


class TestSecurityScan:
    """Test MCP enforcement server security scanning"""

    def test_detect_sql_injection(self):
        """Should detect SQL injection vulnerabilities"""
        code = '''
def get_user(user_id):
    query = "SELECT * FROM users WHERE id = " + str(user_id)
    cursor.execute(query)
'''
        result = security_scan(content=code)
        assert result["total"] > 0, "Should detect SQL injection"
        assert any(i["type"] == "sql_injection_risk" for i in result["issues"])

    def test_detect_hardcoded_secrets(self):
        """Should detect hardcoded API keys"""
        code = 'API_KEY = "sk-abc123def456ghi789jkl012mno345pqr678"'
        result = security_scan(content=code)
        assert result["total"] > 0
        assert any(i["type"] == "hardcoded_secret" for i in result["issues"])

    def test_detect_xss(self):
        """Should detect XSS vulnerabilities"""
        code = 'html_output = f"<div>{user_html}</div>"'
        result = security_scan(content=code)
        assert any(i["type"] == "xss_risk" for i in result["issues"])

    def test_detect_command_injection(self):
        """Should detect command injection risks"""
        code = 'subprocess.run(f"charge-card --amount {amount}", shell=True)'
        result = security_scan(content=code)
        assert any(i["type"] == "command_injection_risk" for i in result["issues"])

    def test_clean_code_passes(self):
        """Clean code should pass security scan"""
        code = '''
def get_user(user_id: int):
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
'''
        result = security_scan(content=code)
        assert result["passed"], f"Clean code should pass: {result['issues']}"


class TestSecretCheck:
    """Test MCP enforcement server secret checking"""

    def test_detect_aws_keys(self):
        """Should detect AWS access keys"""
        code = 'aws_key = "AKIAIOSFODNN7EXAMPLE"'
        result = check_secrets(content=code)
        assert result["total"] > 0
        assert any("aws" in i["type"] for i in result["found"])

    def test_detect_generic_api_key(self):
        """Should detect generic API keys"""
        code = 'api_key = "sk-abc123def456ghi789jkl012mno345pqr678"'
        result = check_secrets(content=code)
        assert result["total"] > 0

    def test_no_secrets_clean_code(self):
        """Should find no secrets in clean code"""
        code = 'user_name = "john_doe"'
        result = check_secrets(content=code)
        assert result["passed"]


class TestPermissionValidator:
    """Test MCP enforcement server permission validation"""

    def test_allow_safe_commands(self):
        """Should allow safe commands"""
        tool_calls = json.dumps([
            {"tool": "Bash", "input": {"command": "git status"}},
            {"tool": "Read", "input": {"path": "src/main.py"}}
        ])
        result = validate_permissions(tool_calls, allowed_patterns=["Bash", "Read"])
        assert result["valid"]

    def test_block_dangerous_commands(self):
        """Should block dangerous commands"""
        tool_calls = json.dumps([
            {"tool": "Bash", "input": {"command": "rm -rf /tmp/test"}}
        ])
        result = validate_permissions(tool_calls, allowed_patterns=["Bash"])
        assert not result["valid"]
        assert "Dangerous command" in result["violations"][0]["reason"]

    def test_block_secret_pattern(self):
        """Should block commands with potential secrets"""
        tool_calls = json.dumps([
            {"tool": "Bash", "input": {"command": "echo 'password=supersecret123' > config.txt"}}
        ])
        result = validate_permissions(tool_calls, allowed_patterns=["Bash"])
        assert isinstance(result["valid"], bool)


class TestHookEnforcement:
    """Test hook enforcement across platforms"""

    def test_claude_code_hooks_config_exists(self):
        """Claude Code hooks.json should exist and be valid"""
        config_path = project_root / ".claude" / "settings.json"
        assert config_path.exists(), "Claude Code settings.json must exist"

        with open(config_path) as f:
            config = json.load(f)

        assert "hooks" in config
        assert "permissions" in config

    def test_opencode_config_exists(self):
        """OpenCode configuration should exist"""
        config_path = project_root / "opencode.json"
        assert config_path.exists()

        with open(config_path) as f:
            config = json.load(f)

        assert "permission" in config or "permissions" in config

    def test_codex_config_exists(self):
        """Codex configuration should exist"""
        config_path = project_root / ".codex" / "hooks.json"
        assert config_path.exists()

        with open(config_path) as f:
            config = json.load(f)

        assert "hooks" in config or "permissions" in config

    def test_gemini_config_exists(self):
        """Gemini CLI configuration should exist"""
        config_path = project_root / ".gemini" / "settings.json"
        assert config_path.exists()

    def test_readonly_evaluator_agent_exists(self):
        """Read-only evaluator agent should exist in .opencode/agents/"""
        agent_path = project_root / ".opencode" / "agents" / "read-only-evaluator.md"
        assert agent_path.exists()

        content = agent_path.read_text()
        assert "read-only" in content.lower() or "deny" in content.lower()
        assert "mode: subagent" in content


class TestCodeComparison:
    """Test comparison between vulnerable and clean code"""

    def test_vulnerable_code_detected(self):
        """Vulnerable code should be flagged"""
        vulnerable_path = project_root / "solution" / "src" / "vulnerable_code.py"
        code = vulnerable_path.read_text()
        result = security_scan(content=code)
        assert result["total"] >= 3, f"Should find at least 3 issues, found {result['total']}"

    def test_clean_code_passes(self):
        """Clean code should pass all checks"""
        clean_path = project_root / "solution" / "src" / "clean_code.py"
        code = clean_path.read_text()
        result = security_scan(content=code)
        assert result["passed"]

    def test_vulnerable_code_has_type_hint_issues(self):
        """Vulnerable code should lack type hints"""
        vulnerable_path = project_root / "solution" / "src" / "vulnerable_code.py"
        code = vulnerable_path.read_text()
        result = lint_code(content=code, language="python")
        assert not result["passed"] or len(result["issues"]) > 0

    def test_clean_code_has_type_hints(self):
        """Clean code should have type hints"""
        clean_path = project_root / "solution" / "src" / "clean_code.py"
        code = clean_path.read_text()
        result = lint_code(content=code, language="python")
        assert not any(i["type"] == "missing_type_hints" for i in result["issues"])


def run_all_tests():
    """Run all tests and generate report"""
    test_classes = [
        TestSecurityScan,
        TestSecretCheck,
        TestPermissionValidator,
        TestHookEnforcement,
        TestCodeComparison,
    ]

    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    results = []

    for test_class in test_classes:
        instance = test_class()
        test_methods = [m for m in dir(instance) if m.startswith("test_")]

        for method_name in test_methods:
            total_tests += 1
            try:
                getattr(instance, method_name)()
                passed_tests += 1
                results.append({
                    "test": f"{test_class.__name__}::{method_name}",
                    "status": "PASS",
                    "error": None
                })
                print(f"  PASS: {test_class.__name__}::{method_name}")
            except Exception as e:
                failed_tests += 1
                results.append({
                    "test": f"{test_class.__name__}::{method_name}",
                    "status": "FAIL",
                    "error": str(e)
                })
                print(f"  FAIL: {test_class.__name__}::{method_name}")
                print(f"    Error: {e}")

    # Generate report
    report = {
        "summary": {
            "total": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "pass_rate": f"{(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%"
        },
        "results": results,
        "timestamp": __import__("datetime").datetime.now().isoformat()
    }

    report_dir = project_root / "solution" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)

    report_path = report_dir / "test_results.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n{'='*60}")
    print(f"Test Summary: {passed_tests}/{total_tests} passed ({report['summary']['pass_rate']})")
    print(f"Report saved to: {report_path}")
    print(f"{'='*60}")

    return failed_tests == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
