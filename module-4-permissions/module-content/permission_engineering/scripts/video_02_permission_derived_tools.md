# Video 2 — Derive Tool Access from Production Permissions

**Target runtime:** 7 minutes  
**Teaching purpose:** Show how trusted entitlements should minimize the tools
offered to the model without replacing runtime authorization.

## Opening

A production harness should not present every connected tool to every user.
The available catalog should reflect what the authenticated principal can
plausibly use under production policy.

If a contractor can create, read, edit, and submit their own permit
applications, the model serving that contractor does not need `issue_permit`
or `revoke_permit`. If an incident responder cannot reassign incidents, the
model does not need `reassign_incident` in that session.

This is least-privilege catalog shaping.

## Build from the production source of truth

The sequence begins outside the model:

```text
verified session or workload identity
                |
                v
roles, groups, scopes, tenant, elevation
                |
                v
production permission mappings
                |
                v
filtered model tool catalog
```

The filter should consume the same stable permission names used by the
application. In the permit exercise, `create_application` maps to
`permit.create`; `approve_application` maps to `permit.approve`; and
`issue_permit` maps to `permit.issue`.

Roles then receive explicit grants. A supervisor has `permit.approve` but not
`permit.issue`. An administrator has issuance and revocation permissions, but
does not automatically inherit every conceivable action. This is an important
least-privilege point: the role name “administrator” is not a wildcard. Only
the permissions in the reviewed set count.

Open `examples/permission_aware_catalog.py`. The catalog builder takes a
trusted principal and the complete tool list. For each tool, it finds the
permission that could make the tool useful to that role. Unknown roles receive
an empty catalog. A coverage assertion fails when a dispatchable tool and the
policy mapping drift apart.

That last check turns a dangerous omission into a deployment failure. A new
tool without a policy rule must not become implicitly public.

## Resource-scoped permissions complicate filtering

Catalog construction often happens before the model chooses a resource. Alex,
a contractor, may edit `P-1042` because Alex owns it. Alex may not edit
`P-2095`, which belongs to someone else.

Should `edit_application` be visible? Yes, because Alex can legitimately use
it for at least some resources. The catalog can determine potential authority
from `permit.edit_own`, but only the runtime decision can compare the requested
application's trusted `owner_user_id` with Alex's authenticated user ID.

This gives us an essential distinction:

- catalog shaping asks whether this tool could be relevant under current
  entitlements;
- invocation authorization asks whether this exact call is allowed now.

The same issue appears with tenants, environments, regions, classifications,
and workflow states. A user may have `database.query` for an analytics tenant
but not a payroll tenant. One tool name cannot express that full decision.

## Why hidden is not denied

Removing a tool from the model catalog reduces selection opportunities. It can
also reduce prompt-injection blast radius and help the model choose accurately.
Those are valuable controls.

But hiding a tool is not a security boundary.

A stale session may hold an old catalog. A caller may construct a request
directly. Another application path may reach the same dispatcher. A grant can
be revoked between model cycles. And downstream services may expose the
operation through another interface.

Therefore the dispatcher must still authorize every proposal. The production
claim is not “the model cannot see the tool.” It is “the protected operation
cannot execute without a current allow decision.”

The Module 4 demo intentionally exposes identical tools in `basic` and
`permissions` modes. That makes authorization the only experimental variable.
For a production deployment, add catalog minimization in front of the same
runtime boundary; do not remove the boundary.

## Internal capabilities require policy too

Some tools are harness mechanics rather than business operations. The demo's
`load_skill` tool is governed by a strict catalog allowlist rather than the
incident business-permission matrix.

That does not mean internal tools are universally trusted. Each capability
needs an explicit governance path. A skill loader needs path and name
allowlisting. A memory tool needs data-scope controls. A shell or code tool
needs especially narrow sandbox and approval policy. “Internal” must never
mean “unrestricted.”

## Credentials must match the decision

There is another production layer below the harness. If every allowed call is
executed with one shared administrator credential, a bug in the dispatcher has
an enormous blast radius.

Prefer delegated user credentials, narrowly scoped workload identities, or a
broker that issues operation-specific credentials where the architecture
supports them. The downstream service should independently enforce access.
Never respond to a denial by retrying with a broader credential.

## Closing

Production permissions should shape what the model can propose, but the catalog
is only the first reduction of capability.

The durable pattern is:

> Minimize before inference. Authorize again before execution.

Next, we will implement that second decision using the trusted subject, exact
action, requested resource, and current context.

## On-screen repository anchors

- `solution/permissions.py`: permission names and role grants
- `solution/tools.py`: complete business-tool inventory
- `examples/permission_aware_catalog.py`: production catalog extension
- `exercise-permisions-starter/INSTRUCTIONS.md`: exact exercise matrix
