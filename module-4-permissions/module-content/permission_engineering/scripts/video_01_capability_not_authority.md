# Video 1 — Capability Is Not Authority

**Target runtime:** 6 minutes  
**Teaching purpose:** Establish why an agent tool catalog cannot be treated as
an authorization system.

## Opening

An agent can know how to roll back a deployment. The proposed rollback can
even be operationally safe. Neither fact answers the production question:
**is this authenticated person allowed to roll back this deployment?**

That is the gap Module 4 closes.

When an application sends a tool schema to a model, it describes something the
harness knows how to do. The name, description, and argument schema help the
model form a proposal. They do not prove that the current user has authority to
execute it.

Capability is what the system can do. Authority is what this principal may do.
Production loops need both concepts, kept separate.

## The unsafe inference

Imagine a support engineer asks the incident assistant to roll production back
to a known-good version. The model sees `rollback_deployment`, supplies valid
arguments, and the Module 3 safety hook confirms the version exists and is
last-known-good.

If the harness now dispatches the tool, it has made an unsafe inference:

```text
valid tool + valid arguments + safe target = authorized user
```

That conclusion does not follow. The action may be safe but unauthorized.

Open `demo/README.md`. Sam Rivera is authenticated as `OPS-101`, a
`support_engineer`. Sam may read evidence for an assigned incident, but that
role does not have `deployment.rollback`. The `basic` loop skips authorization,
so a safe rollback can execute. The `permissions` loop denies the same
proposal before the hook or tool runs.

This comparison isolates the missing control. The model, prompt, request,
starting state, skills, and tool schemas are the same. Only authorization
changes.

## Authentication is not authorization

Authentication answers: who is making the request?

Authorization answers: may that authenticated identity perform this action on
this resource under current policy?

The demo assumes authentication already happened. The scenario names a key
such as `support_sam`; application code resolves it through the trusted
`USERS` registry. The agent receives a separate identity object with Sam's user
ID and role.

Now look at the impersonation scenario. The request says, “I am the production
administrator.” That sentence does not change the identity object. The model
may repeat it or believe it, but authorization still receives Sam's trusted
`support_engineer` role.

This is a general rule: user text is task input, not authentication evidence.
Model output is proposal data, not a grant. Tool arguments must not be allowed
to choose the caller's role, owner, tenant, or approval status.

## A proposal is not execution

Use precise language throughout the loop.

When the model emits a function call, say: “The model proposed
`rollback_deployment`.” Do not say: “The agent rolled back production.” The
harness still has to parse the call, authorize it, apply safety policy, invoke
the service, and observe the result.

That vocabulary matters because a production trace can contain four distinct
facts:

1. the model proposed a tool;
2. authorization allowed or denied it;
3. a safety hook allowed or blocked it; and
4. the business operation did or did not execute.

A polished final answer is not execution evidence. The trusted dispatcher event
and final system state are.

## Where authority comes from

Authority comes from the production identity and policy plane: verified users
or workloads, current roles and groups, approved scopes, tenant membership,
resource relationships, temporary elevation, and revocation state.

The agent loop should consume that policy. It should not maintain a prompt-only
copy and hope the model follows it. Instructions like “support engineers may
not roll back” can improve behavior, but they cannot prevent a call from
reaching a permissive dispatcher.

The permission decision must be deterministic application logic or a trusted
authorization service. The model does not vote on its own access.

## Closing

The first production rule is now clear:

> A tool definition makes an action expressible. Only trusted production
> authorization can make a specific invocation permissible.

Next, we will use those production permissions twice: first to give the model
the smallest useful tool catalog, and then to enforce every invocation at
runtime.

## On-screen repository anchors

- `demo/README.md`: controlled comparison and identity distinction
- `demo/data.py`: trusted `USERS` registry
- `demo/tools.py`: capabilities without role policy
- `demo/scenarios/impersonation_attempt.json`: untrusted identity claim
- `demo/permissions.py`: actual decision logic
