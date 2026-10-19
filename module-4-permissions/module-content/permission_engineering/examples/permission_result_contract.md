# Authorization Decision and Tool-Result Contract

The policy decision, execution event, and model-facing tool result serve
different consumers. Keep them distinct.

## Internal decision

```json
{
  "decision": "DENY",
  "subject_id": "OPS-101",
  "action": "rollback_deployment",
  "required_permission": "deployment.rollback",
  "resource_type": "incident",
  "resource_id": "INC-2048",
  "relationship": "assigned",
  "reason_code": "MISSING_PERMISSION",
  "policy_version": "incident-authz-17",
  "evaluated_at": "2026-10-18T14:20:00Z"
}
```

Required semantics:

- `ALLOW` is the only result that may proceed.
- `DENY`, `ERROR`, `INDETERMINATE`, missing, malformed, and expired decisions
  stop the protected operation.
- The decision applies only to its exact subject, action, resource, context,
  and freshness window.
- An `ALLOW` for one call cannot authorize another call.

## Model-facing denial

```json
{
  "status": "permission_denied",
  "executed": false,
  "tool": "rollback_deployment",
  "required_permission": "deployment.rollback",
  "resource_id": "INC-2048",
  "reason": "The authenticated role cannot roll back deployments."
}
```

The harness returns this as `function_call_output` using the original call ID.
The result lets the model continue truthfully without giving the model a way
to reinterpret denial as approval.

## Execution event

```json
{
  "proposal_id": "call_abc123",
  "tool": "rollback_deployment",
  "permission_check": "DENIED",
  "tool_executed": false,
  "result_status": "permission_denied",
  "policy_version": "incident-authz-17",
  "latency_ms": 4
}
```

Security logs may retain more detail than the model sees. Apply data retention,
access control, and redaction rules to the logs themselves.

## Outcome vocabulary

| Outcome | Meaning | May dispatch? |
| --- | --- | --- |
| `ALLOWED` | Policy explicitly granted this exact call | Yes, after other gates |
| `DENIED` | Policy explicitly refused it | No |
| `ERROR` | No usable policy decision was obtained | No |
| `NOT PERFORMED` | The comparison mode skipped authorization | Only in an intentionally unsafe teaching baseline |
| `NOT REQUESTED` | The model never proposed the action | No decision exists |

Never describe `NOT REQUESTED` as allowed, denied, or blocked. Never describe
`NOT PERFORMED` as an authorization success.

## Information-disclosure rule

A denial should be actionable without revealing protected facts. Depending on
the application, “not found or not permitted” may be safer than confirming that
a resource exists. Keep rich diagnostic details in restricted audit evidence,
not automatically in model context or user-facing text.
