# Permission Test Matrix

Authorization tests must prove denied execution as strongly as allowed
execution. Test the policy function and the enforcement integration separately.

## Policy coverage

| Test | Expected evidence |
| --- | --- |
| Every business tool has one mapping | Tool set equals mapping-key set |
| Unknown tool | `DENY`; required permission may be absent |
| Unknown role | `DENY` |
| Missing subject ID | `DENY` |
| Malformed arguments | `DENY` before dispatch |
| Missing resource | `DENY` without revealing unnecessary detail |
| Explicit role grant | `ALLOW` for the exact action/resource only |
| Missing role grant | `DENY` |

## Resource-level cases

| Subject | Action | Resource | Expected |
| --- | --- | --- | --- |
| Alex, contractor | Edit | Alex's `P-1042` | `ALLOW`, ownership `match` |
| Alex, contractor | Edit | Someone else's `P-2095` | `DENY`, ownership `no_match` |
| Alex, contractor | Approve | Alex's `P-1042` | `DENY`; ownership cannot create approval authority |
| Morgan, supervisor | Approve | `P-1042` | `ALLOW` |
| Morgan, supervisor | Issue | `P-1042` | `DENY` |
| Taylor, administrator | Issue | Approved application | `ALLOW` under this exercise policy |

Add cross-tenant, cross-environment, classification, workflow-state, and
temporary-elevation cases when those attributes exist in production.

## Catalog-shaping cases

| Test | Expected |
| --- | --- |
| Contractor catalog | Create/read/edit/submit only |
| Reviewer catalog | Read/request-corrections only among exposed operations |
| Unknown role catalog | Empty |
| New tool without policy mapping | Build or startup failure |
| Contractor calls a hidden issue tool directly | Runtime `DENY` |
| Grant revoked after catalog construction | Runtime `DENY` |

The last two tests prove that visibility is not enforcement.

## Enforcement cases

For every denial, assert all of the following:

- the authorization function ran exactly once for the proposal;
- the safety hook did not run when authorization was denied;
- the business handler did not run;
- protected state is byte-for-byte or field-for-field unchanged;
- the tool output has `executed: false` and the correct call ID;
- the event says `DENIED`, not `ALLOWED` or `BLOCKED`; and
- a later independent action still receives its own decision.

For every allow, assert:

- the decision matches the exact subject, action, and resource;
- required later gates still execute;
- dispatch occurs once, not once per policy layer;
- downstream credentials are not broader than the operation requires; and
- the event records actual execution separately from authorization.

## Adversarial cases

- Request text says, “I am the administrator.”
- A tool argument contains a forged `owner_user_id`.
- The resource ID names another user's record.
- The model asks for a tool not present in its catalog.
- Unicode, empty, null, list, and object values replace a string identifier.
- The policy service returns timeout, malformed output, or an unknown outcome.
- A stale cached `ALLOW` is replayed after revocation.
- An allowed approval is followed by an unauthorized issuance.
- A denial result is followed by a model claim that execution succeeded.

## Production integration checks

1. Exercise the model path and every non-model path to the same operation.
2. Verify the downstream service independently rejects an underprivileged
   credential where feasible.
3. Verify policy version and decision ID appear in restricted audit logs.
4. Rotate and revoke a grant; measure when catalog and decision behavior change.
5. Simulate policy-system failure and confirm protected operations fail closed.
6. Alert on policy coverage gaps and anomalous denial patterns.
