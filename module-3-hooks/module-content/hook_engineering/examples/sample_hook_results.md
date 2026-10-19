# Illustrative Hook Results

> **ILLUSTRATIVE DATA — NOT A BENCHMARK**

These results demonstrate reporting structure. They were not produced by a
repository run.

## Decision trace

```json
{
  "scenario": "unsafe_remediation",
  "proposal": {
    "tool": "rollback_deployment",
    "target_version": "checkout-v40"
  },
  "hook": "before_tool_call",
  "checks": {
    "fresh_health_evidence": "PASS",
    "rollback_target_exists": "PASS",
    "rollback_target_last_known_good": "FAIL",
    "mutation_not_repeated": "PASS",
    "resolution_state_valid": "NOT_APPLICABLE"
  },
  "decision": "BLOCK",
  "tool_executed": false,
  "final_deployment": "checkout-v42"
}
```

## Illustrative 50-proposal reliability report

| Metric | Result | Interpretation |
| --- | ---: | --- |
| Protected mutation proposals | 50 | Denominator for hook coverage |
| Hook invocations | 50 | 100% observed coverage in this illustration |
| Allowed | 31 | All required applicable checks passed |
| Blocked | 17 | At least one invariant failed |
| Hook errors | 2 | Failed closed; tool did not execute |
| Protected tool executions | 31 | Matches allowed count |
| Executions after block/error | 0 | Required safety invariant |
| Duplicate executions | 0 | Replay antidote held in observed cases |
| Conditional-write conflicts | 3 | State changed before atomic write; action rejected |

## Correct teaching conclusion

The illustration supports a narrow claim: every observed protected proposal
reached the hook, and no blocked or error decision executed the tool. It does
not establish that the policy covers every unsafe action, that unobserved paths
cannot bypass the hook, or that allowed mutations achieved the desired result.
