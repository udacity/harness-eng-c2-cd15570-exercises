# Hook Result Contract

## Minimal course structure

```python
@dataclass
class HookResult:
    allowed: bool
    violations: list[str]
    checks: dict[str, bool]
```

This structure is sufficient for the Module 3 demo and exercise. `allowed` is
true only when no violation exists. `violations` gives actionable feedback, and
`checks` records each named result.

## Recommended production structure

```json
{
  "decision": "BLOCK",
  "hook": "before_tool_call",
  "policy_version": "incident-mutation-3.2.0",
  "tool": "rollback_deployment",
  "input_fingerprint": "sha256:<safe-placeholder>",
  "checks": [
    {
      "name": "rollback_target_last_known_good",
      "status": "FAIL",
      "code": "TARGET_NOT_LAST_KNOWN_GOOD",
      "message": "Rollback target is not marked last-known-good."
    },
    {
      "name": "resolution_state_valid",
      "status": "NOT_APPLICABLE"
    }
  ],
  "tool_executed": false
}
```

## Why four check states help

| Status | Meaning |
| --- | --- |
| `PASS` | The check applied and its invariant held. |
| `FAIL` | The check applied and its invariant did not hold. |
| `ERROR` | The check could not establish a safe result. Fail closed. |
| `NOT_APPLICABLE` | The check does not govern this tool or action. |

The incident demo represents a non-applicable check as `True` because its check
returns no violations. That is adequate for a small binary teaching structure,
but a production trace should avoid reporting “passed” when the check did not
apply.

## Contract invariants

- `ALLOW` requires every required applicable check to be `PASS`.
- Any `FAIL` or `ERROR` produces `BLOCK`.
- `NOT_APPLICABLE` never converts another failure into allow.
- The result does not execute the tool; the dispatcher acts on it.
- A `BLOCK` result must reach the model as evidence while the business tool
  remains uncalled.
- Tool execution evidence is recorded separately from the hook decision.
- Messages are safe for their audience and do not contain secrets.

## Separate decisions

Keep these fields distinct:

```text
call parsed
caller authorized
validity hook executed
hook allowed
tool executed
postcondition passed
final response accepted
```

Collapsing them into one `success=true` hides which boundary produced evidence.
