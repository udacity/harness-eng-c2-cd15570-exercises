# Permission Design Workbook

Use this workbook before connecting any production tool to a model loop. One
row represents one proposed action, not an entire conversation or plan.

## 1. Inventory the protected operations

Start from the real application and downstream APIs. Do not invent a parallel
permission system only for the agent.

| Tool | Production operation | Read or write | Resource type | Side effect |
| --- | --- | --- | --- | --- |
| `rollback_deployment` | Roll back deployment | Write | Incident/service | Changes production version |
| `update_incident_status` | Change incident status | Write | Incident | Changes workflow state |
| `get_incident` | Read incident header | Read | Incident | Discloses incident data |

Questions:

- Which service owns the operation?
- What permission protects the equivalent UI or API path?
- Does the tool combine operations that need different grants?
- Can the tool reach multiple tenants, environments, or resource classes?
- Which service identity or delegated credential will execute it?

Split a tool when one schema would blur materially different permissions.

## 2. Define the trusted subject

Record the origin and freshness of every identity attribute.

| Attribute | Trusted source | Never accept from |
| --- | --- | --- |
| User ID | Verified session or access token | Prompt text |
| Workload ID | Workload identity platform | Model output |
| Role/group | Identity or authorization service | Tool arguments |
| Tenant | Verified session and server-side membership | User-supplied tenant alone |
| Temporary elevation | Approved, unexpired elevation record | “My manager approved” text |

The harness may tell the model which identity is active for usability, but the
model's copy is not the authorization input. The enforcement code receives a
separate trusted principal object.

## 3. Map action to permission

Use stable production permission names.

| Tool | Ordinary permission | Scoped exception |
| --- | --- | --- |
| `get_incident` | `incident.read` | `incident.read_assigned` |
| `rollback_deployment` | `deployment.rollback` | None |
| `reassign_incident` | `incident.reassign` | None |

Coverage rule:

```text
every dispatchable business tool
        == every authorization mapping key
        == every governed catalog entry
```

A new tool without a mapping must be unavailable and denied, not implicitly
public.

## 4. Identify resource and contextual attributes

For each call, specify which values come from parsed arguments and which must
be resolved from trusted state.

```text
proposal: get_incident(incident_id="INC-2048")
                 |
                 v
server resolves INC-2048 -> assigned_user_id=OPS-101, tenant=payments
                 |
                 v
compare against authenticated subject and current policy
```

Do not trust `owner_user_id`, `assigned_user_id`, environment, approval state,
or role merely because the model supplied it. Prefer an opaque resource ID in
the proposal and resolve security-relevant attributes server-side.

Consider:

- resource ownership or assignment;
- tenant and environment;
- workflow state;
- time and approved change window;
- risk tier and data classification;
- required human approval;
- credential and policy freshness; and
- separation-of-duty constraints.

## 5. Decide catalog visibility

Classify each tool for the current principal:

| Classification | Catalog action | Example |
| --- | --- | --- |
| No possible grant | Omit | Contractor never sees `issue_permit` |
| Potentially allowed for some resources | Include, then check every call | Contractor sees `edit_application` |
| Globally allowed by current entitlement | Include, then check every call | Responder sees `query_service_logs` |
| Internal harness capability | Govern separately | Strict allowlisted `load_skill` |

Catalog shaping improves least privilege and tool selection. It does not grant
access. Even an included tool must pass invocation authorization.

## 6. Define the runtime decision

Complete one decision record per call:

```text
subject:              OPS-101 / support_engineer
action:               rollback_deployment
required permission:  deployment.rollback
resource:             INC-2048
trusted relationship: assigned to OPS-101
policy version:       incident-authz-17
decision:             DENY
reason code:          MISSING_PERMISSION
```

Use stable reason codes for metrics and a concise user-facing explanation.
Avoid returning hidden role membership, resource existence, or policy internals
when disclosure would be sensitive.

## 7. Place the enforcement point

Required order:

1. Accept a call only from the allowlisted model-tool protocol.
2. Parse and structurally validate the name and arguments.
3. Resolve the current trusted subject and resource attributes.
4. Obtain an authorization decision.
5. On anything other than explicit `ALLOW`, return without dispatch.
6. Run safety and workflow checks for an authorized operation.
7. Invoke the business service with appropriately scoped credentials.
8. Record the decision and actual execution result.

Never execute first and audit later. A denial after a mutation is evidence of
a control failure, not enforcement.

## 8. Plan failure behavior

| Failure | Required behavior |
| --- | --- |
| Unknown tool | Deny; do not dynamically import or dispatch |
| Missing identity | Deny protected access |
| Invalid resource ID | Deny before lookup-dependent execution |
| Missing policy mapping | Deny and alert policy owners |
| Policy timeout/error | Deny affected operation or follow an explicitly reviewed fail-safe design |
| Stale elevation | Deny and require renewal |
| Tool hidden but directly invoked | Runtime authorization still denies |
| Downstream credential lacks access | Preserve denial; never switch to a broader fallback credential |

## 9. Prove the boundary

Minimum evidence:

- every tool has a permission mapping;
- each role has positive and negative cases;
- the same user is tested against owned and unowned resources;
- request-text impersonation does not alter the principal;
- denials leave state unchanged;
- each action in a multi-action request is checked independently;
- policy errors fail closed;
- catalog and runtime decisions use the intended policy version; and
- audit events distinguish `PROPOSED`, `DENIED`, `BLOCKED`, and `EXECUTED`.

## Production review prompt

> If the model, prompt, or user controls this value, can changing it create or
> expand authority? If yes, move the value behind a trusted application
> boundary before shipping.
