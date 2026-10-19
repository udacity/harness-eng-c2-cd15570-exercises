# Video 4 — Compose the Production Enforcement Loop

**Target runtime:** 7 minutes  
**Teaching purpose:** Integrate permissions with validation, safety hooks,
dispatch, controlled feedback, credentials, and audit evidence.

## Opening

Authorization is essential, but it is not the whole production harness. The
loop must compose several controls in an order that preserves each one's job.

The Module 4 incident demo makes that order visible:

```text
model proposal
  -> parse and validate
  -> authorize subject, action, resource
  -> apply mutation safety hook
  -> dispatch tool
  -> record result
  -> return correlated evidence to model
```

Every arrow is a trust boundary.

## Parse and allowlist first

Before policy can reason about a call, the harness must know that it has a
supported tool name and a valid argument object. JSON parsing is not
authorization, but malformed input should never crash the boundary or reach a
business handler.

Strict schemas reduce ambiguity. Runtime validation remains necessary because
model output and other callers are untrusted. Reject missing, extra, empty, or
wrongly typed security-relevant fields.

Use an explicit handler registry. Do not turn an arbitrary model-generated
name into a module import, URL, shell command, or database method.

## Authorize before expensive or sensitive work

Authorization runs next. A denial short-circuits later controls. In the default
incident scenario, Sam lacks `deployment.rollback`, so the harness does not run
rollback safety checks and does not invoke the tool.

This order avoids unnecessary work and reduces information leakage. A user who
cannot act does not need detailed feedback about which last-known-good versions
exist or which safety predicate would have failed.

The decision itself should be narrow: subject, action, resource, relevant
context, and policy version. It should not mutate business state.

## Safety remains independent

An authorization grant answers “may this subject attempt this operation?” It
does not answer “is this operation safe in the current system state?”

Run the `commander_premature_resolution` scenario. Morgan has
`incident.status.update`, so authorization returns `ALLOW`. The Module 3 hook
then sees degraded health and unconfirmed recovery and blocks `RESOLVED`.

The reverse is also possible. Sam's rollback target is safe, but the call is
unauthorized. Both gates must pass.

Use distinct result words:

- `DENIED` means authority was absent;
- `BLOCKED` means a later safety invariant failed;
- `EXECUTED` means dispatch actually occurred; and
- `NOT REQUESTED` means no call existed to decide.

Do not collapse these into a generic failure. Operators need to know which
control acted.

## Dispatch with bounded authority

After authorization and safety, invoke one allowlisted handler. The downstream
credential should carry no more authority than needed.

Ideal architectures preserve end-user delegation or mint a narrowly scoped,
short-lived operation credential. Where a service identity is necessary, the
broker must bind the approved subject, action, resource, tenant, and expiry to
the execution request. The downstream service should validate its own access
policy as defense in depth.

Do not give the model raw credentials. Do not store administrator tokens in
prompt context. Do not retry a service denial with a broader shared secret.

For sensitive writes, protect against time-of-check/time-of-use changes. The
resource can change after policy evaluation. Use transactions, conditional
writes, version checks, or service-side authorization so the state authorized
is the state changed.

## Return controlled evidence

Whether the call is denied, blocked, or executed, return one result matched to
the original call ID. This lets the model continue the task and describe what
actually happened.

The model cannot override a denial. It can explain it, propose an authorized
alternative, or ask the user to obtain access. If the request has multiple
actions, it should still propose each action independently so the harness can
produce distinct decisions.

Model-facing denial details require care. The demo includes subject, required
permission, resource, and reason because those facts are useful in the
classroom. A production application may need a generic “not found or not
permitted” message to avoid revealing resource existence or sensitive policy
structure. Richer details can remain in restricted security logs.

## Record evidence, not conclusions

For every call, log a proposal identifier, trusted subject reference, tool,
resource reference, policy version, decision, reason code, safety outcome,
dispatch outcome, and latency. Protect and retain those logs according to
their sensitivity.

Do not rely on final prose such as “I rolled it back.” Record the actual
dispatcher event and verify final state. The Module 4 summary correctly calls
an unmade action `not requested`, an unchecked basic action `not performed`,
and a rejected proposal `denied`.

## A complete decision table

Use this four-case test during design review:

| Authorized? | Safe? | Outcome |
| --- | --- | --- |
| No | Unknown/not evaluated | Deny; no hook or execution |
| Yes | No | Block; no execution |
| Yes | Yes | Execute through dispatcher |
| Unknown/error | Any | Fail closed; no execution |

The “safe but unauthorized” row is deliberately absent from later evaluation:
authorization denial stops it first.

## Closing

Production reliability comes from composition, not from asking one mechanism
to answer every question.

Authentication establishes the principal. Permissions establish authority.
Hooks establish deterministic safety. Validation establishes shape. The tool
performs the operation. Evidence establishes what happened.

Next, we will test and operate this boundary so new tools, changing policies,
revocation, and failures do not create silent bypasses.

## On-screen repository anchors

- `demo/agent.py`: enforcement order and structured outputs
- `demo/hooks.py`: safety after authorization
- `demo/tools.py`: policy-light dispatcher
- `examples/authorization_boundary_pseudocode.py`: full boundary
- `examples/permission_result_contract.md`: decision vocabulary
