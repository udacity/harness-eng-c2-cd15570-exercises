# Chart and Table Specifications

Use tables and state diagrams for exact comparisons. Do not invent performance
or security-effectiveness percentages.

## Chart 1 — Basic versus permissions trace

**Type:** Two-lane event timeline  
**Purpose:** Isolate authorization in the classroom comparison.

| Stage | Basic | Permissions |
| --- | --- | --- |
| Trusted subject | Sam / OPS-101 | Sam / OPS-101 |
| Tool proposal | Roll back to v41 | Roll back to v41 |
| Permission check | Not performed | Denied |
| Safety hook | Allowed if reached | Not run |
| Tool execution | Yes if hook allows | No |
| Final deployment | v41 | v42 |

**Footnote:** Model behavior can vary; populate a recorded chart only from the
actual run trace.

## Chart 2 — Role-to-operation matrix

**Type:** Binary heatmap  
**Rows:** contractor, reviewer, supervisor, administrator  
**Columns:** create, read, edit, submit, request corrections, approve, reject,
issue, revoke.

Use separate hatching for contractor `_own` grants. Do not display a contractor
read/edit/submit cell as globally allowed.

## Chart 3 — Four control outcomes

**Type:** Decision table

| Authorization | Safety | Execution |
| --- | --- | --- |
| Deny/error | Not evaluated | No |
| Allow | Block | No |
| Allow | Allow/not applicable | Yes, if dispatch succeeds |

Do not include “authorization skipped” as success. It is a deliberately unsafe
baseline condition.

## Chart 4 — Catalog and runtime responsibilities

**Type:** Comparison table

| Dimension | Catalog shaping | Runtime authorization |
| --- | --- | --- |
| Timing | Before model inference | Before every execution |
| Main value | Reduce exposed capability | Enforce current authority |
| Typical inputs | Role/scope and tool mapping | Subject, action, resource, context |
| Handles ownership alone? | Usually no | Yes |
| Security boundary? | Defense in depth | Yes, with downstream enforcement |

## Chart 5 — Authorization test coverage

**Type:** Coverage matrix  
**Rows:** roles and special identity states  
**Columns:** tools, owned resource, other resource, unknown resource, malformed
input, policy failure.

Each cell shows `ALLOW`, `DENY`, or `N/A`. Add an adjacent enforcement column
for dispatcher call count and state change.

## Chart 6 — Operational funnel

**Type:** Counts by stage, using actual environment data only

```text
model proposals
  explicit allows
    safety passes
      dispatch attempts
        confirmed successes
```

Display denials, errors, safety blocks, and downstream failures as side exits.
Never interpret a lower execution count as intrinsically good or bad without
request context.

## Chart 7 — Revocation timeline

**Type:** Event timeline

Markers:

1. grant active;
2. catalog built;
3. grant revoked;
4. cache invalidated;
5. credential expires;
6. attempted call denied.

Annotate the longest interval in which stale authority could remain effective.
Use measured system behavior, not an assumed instant revocation claim.
