# Module Overview: Permission-Aware Tool Access

## Module purpose

This module moves a harness from “the model can call this tool” to “this
authenticated principal is allowed to request this operation on this resource
right now.” Students learn to connect an agent loop to the same production
permission model that protects non-agent application paths.

The key lesson is simple: **capability is not authority**. A model-facing tool
catalog is an interface, not an access-control policy. Production authorization
must remain external to the model and must govern both what the loop exposes
and what the application actually executes.

## Prerequisites

Students should already be able to:

- trace a model/tool loop and its `function_call_output` continuation;
- distinguish model output from trusted application state;
- explain how skills add procedural context without granting authority;
- explain how hooks deterministically block unsafe mutations; and
- read a small Python mapping, dataclass, and unit test.

## Five-video sequence

| Video | Working title | Central question | Target |
| --- | --- | --- | ---: |
| 1 | Capability Is Not Authority | Why is an exposed tool not a permission grant? | 6 min |
| 2 | Derive Tool Access from Production Permissions | How should identity and entitlements shape the catalog? | 7 min |
| 3 | Authorize Every Proposed Invocation | How does subject-action-resource authorization stop execution? | 7 min |
| 4 | Compose the Production Enforcement Loop | How do permissions, hooks, validation, and feedback fit together? | 7 min |
| 5 | Test and Operate Least Privilege | How do teams prove the boundary remains complete and effective? | 6 min |

Approximate total: 33 minutes.

## Conceptual spine

The module develops one production path:

```text
authenticate outside the model
        |
        v
resolve trusted principal and production entitlements
        |
        v
derive least-privilege tool catalog
        |
        v
model proposes a tool call
        |
        v
parse and validate the proposal
        |
        v
authorize subject + action + resource + current context
        |
        +-- DENY/ERROR --> no execution; return structured result
        |
        v
run deterministic safety hook when applicable
        |
        +-- BLOCK --> no execution; return structured result
        |
        v
execute through an allowlisted dispatcher
        |
        v
record evidence and return the correlated result
```

Students should leave able to identify two distinct permission controls:

1. **Capability minimization:** expose only tools plausibly usable under the
   principal's production entitlements.
2. **Invocation authorization:** decide every call from current trusted data
   immediately before dispatch.

The first narrows the model's action surface. The second enforces security.

## Production permission sources

The harness should consume permission facts from the application's trusted
identity and policy plane, such as:

- authenticated user or workload identity;
- role and group memberships;
- OAuth scopes or service entitlements;
- tenant and environment membership;
- resource ownership or assignment;
- temporary elevation and approval records;
- policy version and relevant environmental conditions; and
- current revocation status.

Prompt text, model assertions, tool arguments claiming a role, and prior model
messages are untrusted inputs. They cannot create authority.

## Important distinctions

| Mechanism | Question answered | Must not be confused with |
| --- | --- | --- |
| Authentication | Who is the principal? | Permission to act |
| Catalog shaping | Which tools are reasonable to offer? | Complete authorization |
| Authorization | May this subject perform this action on this resource now? | Whether the action is safe |
| Safety hook | Does this action satisfy deterministic operational invariants? | Whether the subject is allowed |
| Tool validation | Are the name and arguments structurally valid? | Permission or safety |
| Tool execution | What side effect or retrieval occurs? | Any preceding decision |

An action can be authorized but unsafe, safe but unauthorized, both, or
neither. Production execution requires every applicable gate to allow it.

## Repository-specific demonstration

The incident demo compares two modes with identical prompts and tools:

- `basic` performs no authorization check;
- `permissions` runs `check_permission()` before a safety hook or tool.

This controlled experiment proves the value of authorization. Sam may safely
roll back to the last-known-good deployment, but his `support_engineer` role
does not have `deployment.rollback`; the permissions path denies the proposal.
Morgan may update incident status, but the Module 3 hook can still block an
unsafe premature resolution.

The exercise transfers the same pattern to permit applications. A contractor
can edit an application only when the application is owned by that trusted
user. A supervisor can approve but cannot issue. Each proposed action receives
its own decision.

## Production extension beyond the demo

Production loops should not routinely advertise every integration to every
principal. A catalog builder can map trusted entitlements to a smaller set of
tools before the model call. This reduces accidental selection, limits prompt
injection opportunities, and improves tool choice.

Filtering cannot replace enforcement:

- a tool can cover many resources with different owners or tenants;
- access can be revoked after the catalog is built;
- tool arguments determine the specific action and resource;
- workflow state can change between model cycles;
- another execution path may bypass the model-facing catalog; and
- downstream services must still enforce their own permissions.

The runtime policy decision is therefore authoritative. A hidden tool is less
discoverable; a denied tool is not executable.

## Assessment evidence

Students demonstrate mastery by producing:

- a complete role-to-permission and tool-to-permission mapping;
- an ownership-aware, fail-closed decision function;
- a permission-derived tool catalog with documented limitations;
- a before-dispatch enforcement branch that cannot fall through on denial;
- structured events distinguishing proposal, decision, and execution;
- positive, negative, cross-resource, impersonation, and policy-failure tests;
  and
- an explanation of why an allowed first action does not authorize a second.

## Scope boundaries

The repository assumes authentication and uses in-memory state. It does not
implement OAuth, token verification, policy distribution, databases, tenants,
credential brokers, or a production policy engine. Those are discussed as
deployment concerns, not represented as completed features.
