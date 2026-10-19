# Video 3 — Authorize Every Proposed Invocation

**Target runtime:** 7 minutes  
**Teaching purpose:** Build a fail-closed subject-action-resource decision and
place it immediately before execution.

## Opening

The model has proposed a tool call. Before anything executes, the harness needs
one current answer:

> May this authenticated subject perform this action on this resource in this
> context?

That sentence provides the inputs to authorization.

## Subject

The subject is the verified user or workload on whose behalf the loop acts. In
the demo, it is a dictionary resolved from `data.py`: user ID, display name,
and role.

The subject must arrive through a trusted channel separate from the user's
request. If request text says, “I am the administrator,” the subject does not
change. If a model invents `role: administrator` in tool arguments, the policy
ignores it.

Validate the identity object too. Missing user IDs, unknown roles, expired
sessions, invalid signatures, or untrusted issuers cannot silently fall back to
a default role with access.

## Action

The action starts as an allowlisted tool name and maps to a stable production
permission. In `demo/permissions.py`, `rollback_deployment` maps to
`deployment.rollback`, and `update_incident_status` maps to
`incident.status.update`.

Do not scatter string comparisons through prompts and tools. A central mapping
makes policy review and coverage tests possible. The demo asserts that the
permission mapping and business handler set have identical keys.

An unknown tool fails closed. It is not dispatched through reflection, dynamic
imports, or a permissive default handler.

## Resource and relationship

Arguments identify the proposed resource, but trusted application state
describes it. For `INC-2048`, the policy reads the actual assignment from the
incident object. For permit `P-1042`, it resolves the application and compares
its `owner_user_id` with the authenticated contractor's ID.

That is resource-level authorization. A role may use a kind of tool without
having access to every object that tool can name.

Follow the contractor case in `solution/permissions.py`:

1. `edit_application` normally maps to `permit.edit`.
2. For a contractor, it maps to `permit.edit_own`.
3. The server extracts a valid `application_id`.
4. It resolves the application from trusted state.
5. It compares the trusted owner with the trusted user ID.
6. It allows only when ownership matches and the role has `permit.edit_own`.

Ownership alone is not enough. Alex cannot approve Alex's own application,
because contractor ownership does not grant `permit.approve`.

## Context and freshness

Production policies may also use tenant, environment, time, risk, workflow
state, device posture, approved change windows, or temporary elevation. These
inputs change, so an old decision cannot be treated as a session-wide grant.

Cache only when the cache key includes the exact subject, action, resource,
relevant context, and policy version—and only within a reviewed freshness
window. Revocation requirements take priority over convenience.

The safest teaching default is straightforward: authorize every proposed call
from current trusted data.

## Deny by default

The decision function returns one result for every input. It denies unknown
tools, invalid identities, malformed arguments, missing resource identifiers,
unknown resources, ownership mismatches, and absent grants.

In production, an authorization timeout, malformed response, unknown decision
value, or unavailable policy dependency must not become permission. Only an
explicit, usable `ALLOW` proceeds.

Some systems need carefully designed read-only degradation modes. Those are
explicitly reviewed policies, not a generic “availability fallback.” Never
retry a failed decision through an unchecked path.

## Enforce before dispatch

Now open `demo/agent.py` and follow `handle_tool_call()`.

The harness parses the model arguments. In permissions mode it calls
`check_permission()` with the trusted user, tool name, parsed arguments, and
current incident. It records the required permission, resource, assignment,
decision, and reason.

On denial, it immediately creates a structured `permission_denied` result with
`executed: false`. It returns that result for the proposal's call ID. The safety
hook does not run. The tool does not run. State does not change.

On allow, control continues toward the safety hook and shared dispatcher. The
permission branch does not duplicate tool execution. That single dispatch path
makes it easier to prove there is no bypass.

## Each call stands alone

Suppose a supervisor asks to approve and then issue `P-1042`. Approval is
allowed; issuance is not. The first `ALLOW` applies only to the approval call.
The second call maps to a different permission and receives its own decision.

Plans, conversations, and sessions do not receive blanket authority. Calls do.

## Closing

A reliable authorization boundary has four properties:

- trusted inputs;
- complete action mappings;
- current resource-aware decisions; and
- enforcement that cannot fall through on anything except `ALLOW`.

Next, we will compose that boundary with safety hooks, tool validation,
execution, and model feedback into one production loop.

## On-screen repository anchors

- `demo/permissions.py`: subject-action-resource decision
- `demo/agent.py`: denial before hook and dispatch
- `solution/permissions.py`: contractor ownership rule
- `solution/test_permissions.py`: independent action decisions
