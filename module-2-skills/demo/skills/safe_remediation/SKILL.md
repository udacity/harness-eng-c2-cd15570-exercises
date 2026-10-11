---
name: safe_remediation
description: Use when a request asks for a restart, rollback, production mutation, or the safest remediation process.
---

# Safe remediation

## Purpose

Describe a cautious remediation process without claiming that a production
change has been approved, started, completed, or successful. This skill guides
recommendations; it does not grant authority and does not execute tools.

## Preconditions for a production change

Treat every restart, rollback, traffic shift, configuration edit, or deployment
change as proposed until authoritative execution evidence says otherwise.
Before recommending a mutation, require enough current evidence to explain why
that action is safer than continued observation or a narrower diagnostic step.

At minimum, review:

- a fresh health and impact snapshot;
- relevant logs or other evidence about the failing path;
- deployment history and the active version;
- the proposed target and why it is considered last-known-good;
- authorization from the appropriate production responder; and
- a verification and stop plan for after the action.

The mere existence of a last-known-good deployment does not prove that it is
compatible with the current environment, that rollback is authorized, or that
the present deployment caused the incident.

## Recommend one controlled action

Use conditional language: "If the evidence supports the deployment hypothesis
and an authorized responder approves, perform one controlled rollback." Keep a
restart distinct from a rollback; they have different risks and should not be
presented as interchangeable experiments.

Specify only one production mutation at a time. Define the intended observation
before the action, then compare the same health and impact signals afterward.
Do not recommend repeated restarts, repeated rollbacks, or multiple simultaneous
changes in response to an unchanged signal. Multiple mutations destroy the
ability to attribute an observed result and can increase operational risk.

## Verify before continuing

After an authorized action, require fresh evidence rather than assuming
success. Verification should re-check the same service health, error rate, and
failure scope used before the action. Watch for partial recovery, regression,
or impact moving to another path. If the expected improvement is absent, stop
and reassess instead of immediately attempting another mutation.

Separate these states clearly:

- **Proposed:** an action is under consideration.
- **Authorized:** the appropriate responder approved it.
- **Executed:** reliable evidence confirms it occurred.
- **Effective:** post-action measurements show the intended improvement.
- **Recovered:** authoritative state confirms service recovery.
- **Resolved:** the incident has been formally closed.

Never collapse these states into one another. A proposal is not execution, and
execution is not recovery.

## Construct the response

State the current confirmed condition first. Recommend gathering missing
evidence before mutation. If a production action is appropriate, describe it as
a conditional, authorized, single change followed by verification and a stop
condition. Never announce a successful restart, rollback, mitigation, recovery,
or resolution unless the authoritative record explicitly confirms it.
