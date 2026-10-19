# Storyboard — Video 4: Compose the Production Enforcement Loop

**Target runtime:** 7 minutes  
**Visual motif:** A vertical series of gates; only one green path reaches the
side-effect boundary.

## Slide 1 — Ordered controls

**Time:** 0:00–0:45  
**Visual:** Parse → authorize → safety → dispatch → evidence.  
**On-screen text:** Different gates answer different questions.

## Slide 2 — Parse and allowlist

**Time:** 0:45–1:25  
**Visual:** Invalid JSON, unexpected field, and unknown tool fall into a
`tool_error` lane before policy or dispatch.  
**Callout:** Valid shape does not imply permission.

## Slide 3 — Authorization short-circuit

**Time:** 1:25–2:10  
**Visual:** Sam's rollback reaches red `DENY`; the safety and tool stages turn
gray and say `NOT RUN`.  
**Annotation:** Avoid work and sensitive policy detail for unauthorized users.

## Slide 4 — Authorization and safety grid

**Time:** 2:10–3:05  
**Visual:** Four-quadrant matrix.

| | Safe | Unsafe |
| --- | --- | --- |
| Authorized | Execute | Hook blocks |
| Unauthorized | Deny first | Deny first |

**Examples:** Morgan rollback; Morgan premature resolution; Sam rollback.

## Slide 5 — Bounded dispatch

**Time:** 3:05–3:50  
**Visual:** One allowlisted dispatcher sends one operation with a narrow
credential to the business service. Broad admin key and duplicate dispatch are
crossed out.  
**Callout:** Downstream enforcement remains valuable.

## Slide 6 — State consistency

**Time:** 3:50–4:25  
**Visual:** Resource version `v7` is authorized; conditional write rejects if
current version becomes `v8`.  
**On-screen text:** Authorize the state you mutate.

## Slide 7 — Controlled feedback

**Time:** 4:25–5:10  
**Visual:** Three model-facing result envelopes with matching call IDs:
`permission_denied`, `blocked`, `executed`.  
**Annotation:** The model may explain or adapt, never override.

## Slide 8 — Evidence layers

**Time:** 5:10–5:55  
**Visual:** Timeline rows for proposal, policy decision, hook result, dispatch,
and final state. Final prose appears as a separate non-authoritative row.  
**Callout:** Record facts, not inferred success.

## Slide 9 — Complete vocabulary

**Time:** 5:55–6:30  
**Visual:** Status legend:

- `NOT REQUESTED`
- `NOT PERFORMED`
- `DENIED`
- `BLOCKED`
- `EXECUTED`

**Teaching note:** Ask learners which statuses imply a permission decision.

## Slide 10 — Takeaway

**Time:** 6:30–7:00  
**On-screen build:** Identity establishes who. Permissions establish authority.
Hooks establish safety. Tools act. Evidence proves.  
**Transition:** Next: continuously test and operate the boundary.

## Production notes

- Reuse gate colors from Module 3 but add a distinct authorization shield.
- Do not show safety as part of the role matrix.
- Repository capture: `demo/agent.py` denial and hook branches.
