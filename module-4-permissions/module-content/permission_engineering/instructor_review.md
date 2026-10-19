# Instructor Review Packet

## Review status

This packet is ready for technical, instructional-design, security, and visual
review. Resolve every blocking item before recording.

## Decisions requiring approval

### 1. Central thesis

Approve this exact statement:

> A production loop derives its available tools from trusted production
> entitlements and independently authorizes every proposed invocation before
> execution. Catalog filtering reduces capability; runtime authorization
> enforces authority.

This wording intentionally avoids claiming that hidden tools are secured only
because the model cannot see them.

### 2. Demo versus production distinction

The demo exposes identical tools across `basic` and `permissions` so
authorization is the only experimental variable. The scripts then teach
permission-derived catalog minimization as the production extension.

Confirm that instructors will state both facts. Omitting either creates
confusion between controlled evaluation design and deployment guidance.

### 3. Authentication scope

The repository assumes authentication. It does not implement token validation,
login, OAuth, identity federation, or session management. Approve the phrase:
“trusted identity supplied by the application” rather than “the demo securely
authenticates the user.”

### 4. Authorization model

The exercise combines role-based grants with resource ownership. It is not pure
RBAC. Approve subject-action-resource language and the limited use of
“relationship” for assignment and ownership.

### 5. Permission versus safety

Approve the enforcement order:

```text
parse -> authorize -> safety hook -> dispatch
```

The permission gate short-circuits the safety hook on denial. This is both the
repository behavior and the intended teaching point.

## Technical accuracy checklist

- [ ] The support engineer has assigned-only read permissions and no rollback.
- [ ] The responder can roll back but cannot update incident status.
- [ ] The incident commander can update status but cannot reassign.
- [ ] The administrator adds incident reassignment.
- [ ] `load_skill` is governed separately from the business permission matrix.
- [ ] The demo authorization decision runs before the Module 3 mutation hook.
- [ ] A denied call returns `executed: false` and does not mutate state.
- [ ] A permission allow does not bypass safety checks.
- [ ] Contractor read, edit, and submit use `_own` permissions.
- [ ] Permit ownership comes from trusted application data.
- [ ] A supervisor can approve but cannot issue.
- [ ] Each tool call receives an independent decision.
- [ ] The basic mode is called “authorization not performed,” never “allowed.”
- [ ] Model final text is not presented as execution evidence.

## Production-security checklist

- [ ] Catalog filtering is described as defense in depth.
- [ ] Runtime authorization remains mandatory for visible and hidden tools.
- [ ] Unknown tools, roles, resources, and policy outcomes fail closed.
- [ ] Resource and tenant attributes are resolved from trusted systems.
- [ ] Policy freshness and revocation limitations are acknowledged.
- [ ] Downstream credentials are described as bounded and protected from model
      context.
- [ ] Alternate paths and direct service access are included in coverage tests.
- [ ] Denial feedback is reviewed for information disclosure.
- [ ] Authorization logs are themselves treated as sensitive.
- [ ] No claim implies this module alone establishes NIST compliance or zero
      trust architecture.

## Instructional-design checklist

- [ ] Video 1 corrects “tool visible means user allowed.”
- [ ] Video 2 introduces catalog shaping without treating it as enforcement.
- [ ] Video 3 traces subject, action, resource, and current context.
- [ ] Video 4 distinguishes permission denial from safety block.
- [ ] Video 5 tests both policy decisions and dispatcher behavior.
- [ ] Every acronym is defined before use.
- [ ] At least one read-access example prevents a mutation-only framing.
- [ ] The impersonation example clearly separates request text from identity.
- [ ] The multi-action example ends in `APPROVED`, not `PERMIT_ISSUED`.
- [ ] Students see both positive and negative permission tests.

## Recording checklist

- [ ] Reset incident or application state before every comparison.
- [ ] Show the trusted identity source before showing request text.
- [ ] State that live model proposals can vary.
- [ ] Do not pre-announce allow or deny unless a proposal actually occurred.
- [ ] Pause on the permission decision before revealing execution.
- [ ] Use `NOT REQUESTED`, `NOT PERFORMED`, `DENIED`, `BLOCKED`, and
      `EXECUTED` consistently.
- [ ] Do not display `.env`, API keys, local home paths, or real identities.
- [ ] Label sample dashboards and traces illustrative.
- [ ] Record terminal text at an accessible size.

## Suggested live sequence

1. Open `demo/data.py`; identify Sam's trusted user ID and role.
2. Open `demo/permissions.py`; follow tool-to-permission mapping.
3. Run `unauthorized_rollback`; compare unchecked and denied execution.
4. Run `commander_rollback`; show authorization then safety then execution.
5. Run `commander_premature_resolution`; show allow then safety block.
6. Run `unassigned_read`; show resource-level assignment.
7. Run `impersonation_attempt`; contrast words with trusted identity.
8. Open `solution/permissions.py`; transfer to contractor ownership.
9. Open `examples/permission_aware_catalog.py`; explain the production
   extension and its limitations.
10. End on the three evidence questions from Video 5.

## Discussion prompts

1. Which production system is the source of truth for identity and grants?
2. Which tools should never appear for a given role, and why?
3. Which visible tools still need resource-level checks?
4. What happens if policy is unavailable?
5. How quickly must revocation affect catalogs, caches, and credentials?
6. Can an allowed operation still be unsafe? Can a safe one be unauthorized?
7. How do we prove denial prevented every side-effect path?
8. What information should a denial reveal to the model and user?

## Known limitations to say aloud

- Identities and resources are fictional and in memory.
- Authentication is assumed.
- Policy evaluation is local Python rather than a distributed policy service.
- The catalog-filter example is instructional and not wired into the demo.
- The tools simplify business workflow validation.
- No real credential broker, tenant system, revocation stream, or transaction
  boundary is implemented.
- Passing unit tests does not replace threat modeling, integration testing,
  penetration testing, or organizational access reviews.

## Final sign-off

| Reviewer | Focus | Status | Notes |
| --- | --- | --- | --- |
| Module instructor | Learning sequence | Pending | |
| Repository maintainer | Code alignment | Pending | |
| Security reviewer | Authorization claims | Pending | |
| Instructional designer | Cognitive load and timing | Pending | |
| Visual producer | Accessibility and asset plan | Pending | |
