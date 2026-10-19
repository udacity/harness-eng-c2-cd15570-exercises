# Antidote Design Workbook

An antidote is a deterministic check aimed at one known failure. Use this
worksheet before writing hook code.

## Design sequence

### 1. Name the observed failure

Use a concrete undesirable event:

```text
The agent requested rollback to checkout-v40 even though trusted deployment
history did not mark it last-known-good.
```

Avoid vague labels such as “the agent was unsafe.”

### 2. State the invariant

Write the property that must be true at one boundary:

```text
Immediately before rollback execution, target_version must identify an entry in
trusted deployment history whose last_known_good value is exactly true.
```

The invariant declares time, scope, field, source, and comparison.

### 3. Identify the protected boundary

```text
event: before_tool_call
tool: rollback_deployment
effect prevented: current_deployment mutation
```

Inventory every route to that effect. A second endpoint or background worker
that bypasses the hook remains unprotected.

### 4. Define trusted inputs

| Input | Source | Validation |
| --- | --- | --- |
| Canonical tool name | Harness dispatch table | Exact enum membership |
| `target_version` | Parsed model arguments | Required string, no extras |
| Incident ID | Model argument matched to active incident | Exact equality |
| Deployment history | Application-owned incident state | Expected list/schema |
| Policy version | Deployed configuration | Immutable identifier |

Do not let the model supply both the proposed value and the “trusted” evidence
that approves it.

### 5. Write the predicate

```python
allowed = any(
    item.get("version") == target
    and item.get("last_known_good") is True
    for item in deployment_history
)
```

Keep the check free of model calls, randomness, uncontrolled time, and hidden
mutable globals. If external data is required, resolve and snapshot it before
calling the pure predicate.

### 6. Write actionable failure evidence

```text
Rollback target 'checkout-v40' is not marked last-known-good.
```

Return the failed field and rule without leaking secrets. Evidence should help
the model explain the block or choose a valid recovery path.

### 7. Specify edge semantics

- What is not applicable?
- What happens if state is missing or malformed?
- Are comparisons case-sensitive?
- Does equality pass at the threshold?
- How are numbers represented?
- How are equivalent calls canonicalized?
- How fresh must evidence be?
- Can state change between check and execution?

### 8. Create the truth table

| Target exists | Marked last-known-good | Expected decision |
| --- | --- | --- |
| no | no | block: absent + not last-known-good |
| yes | no | block: not last-known-good |
| yes | yes | allow if every other invariant passes |

### 9. Add boundary and bypass tests

- known valid target;
- known invalid target;
- unknown target;
- missing target;
- wrong incident ID;
- malformed history;
- repeated equivalent mutation;
- direct tool dispatch path that attempts to skip the hook; and
- state change between check and write.

### 10. State residual risk

This antidote does not prove that the target is currently healthy, that the
caller is authorized, that rollback will succeed, or that deployment history
cannot change before the write. Those properties require other controls.

## Blank template

```text
Known failure:
Invariant:
Lifecycle event:
Protected tool/effect:
Trusted inputs and sources:
Canonicalization:
Predicate:
Violation evidence:
Not-applicable behavior:
Error behavior:
Boundary cases:
Bypass paths:
Atomicity requirement:
Tests:
Residual risk:
Owner/version:
```
