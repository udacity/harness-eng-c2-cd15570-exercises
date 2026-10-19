# Diagram Concepts

## Visual thesis

The module's recurring picture is a permission shield between a model proposal
and a production side effect. The shield receives trusted identity and resource
data from outside the model conversation.

## Concept 1 — Tool card versus permission token

Show a neutral tool card labeled `rollback_deployment`. Beside it, show a
signed entitlement token labeled `deployment.rollback`. The tool card means
the harness supports the operation; only the current trusted token can
participate in an allow decision.

Avoid keys, crowns, or “admin magic” imagery. Those suggest role names confer
unbounded access.

## Concept 2 — Catalog sieve

A complete catalog of business tools enters a sieve labeled “trusted
entitlements.” The output contains only the principal's potentially usable
tools. A second, heavier gate remains before production.

This diagram must keep both controls visible. Never end the drawing at the
catalog filter, which would incorrectly imply hiding equals enforcement.

## Concept 3 — Identity split screen

Left side: verified session resolves `OPS-101 / support_engineer`. Right side:
request bubble says, “I am the production administrator.” A hard trust boundary
prevents the sentence from reaching the role field.

Caption: “Task text cannot rewrite authentication.”

## Concept 4 — Resource relationship

Place Alex at the center with two permit cards:

- `P-1042`, trusted owner `USR-101`, green relationship line;
- `P-2095`, trusted owner `USR-999`, red mismatch line.

The same `edit_application` action appears above both. This isolates why
role-only policy is insufficient.

## Concept 5 — Layered gates

Use five labeled gates:

1. protocol and schema;
2. authorization;
3. deterministic safety;
4. allowlisted dispatch;
5. downstream service.

Gray out every downstream gate after a denial. A safety block uses a different
icon and label from an authorization denial.

## Concept 6 — Evidence ledger

Use a ledger rather than a chat transcript:

| Stage | Sample evidence |
| --- | --- |
| Proposal | `rollback_deployment` requested |
| Permission | `DENIED`, policy version 17 |
| Hook | Not run |
| Dispatch | Not executed |
| State | Deployment unchanged |

Place final model prose below a divider labeled “narrative, not execution
evidence.”

## Concept 7 — Policy lifecycle

Show one reviewed bundle moving through development, deployment, and operation:
tool schema, handler, action mapping, role grants, resource predicates, tests,
credential scopes, policy version, and metrics.

Use this to teach that access control drift is a configuration and operations
problem, not only a coding problem.

## Motion rules

- Amber pulse: model proposal.
- Blue input lines: trusted identity, policy, and resource state.
- Red stop: explicit denial or unusable decision.
- Purple stop: deterministic safety block.
- Green motion: only after explicit authorization and every later gate passes.
- Gray stage: not performed.

Always pair color with text and shape for accessibility.
