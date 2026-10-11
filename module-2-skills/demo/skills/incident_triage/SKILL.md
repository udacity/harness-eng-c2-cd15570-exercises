---
name: incident_triage
description: Use when a request requires investigating an incident, separating evidence from hypotheses, or choosing the next diagnostic checks.
---

# Incident triage

## Purpose

Turn the supplied incident state into a disciplined first assessment. The goal
is to preserve the difference between observations, hypotheses, and unknowns
while identifying the next evidence that would narrow the investigation. Do
not use confident language merely because two events occurred close together.

## Establish the current state

Begin with the incident identifier, environment, affected service, declared
incident status, current health, and measured impact. Record the active
deployment and any supplied last-known-good deployment. Treat these values as a
snapshot, not as proof about what happened before or what will happen next.

Use explicit evidence language:

- **Confirmed:** directly supplied by the authoritative incident record or a
  current tool result.
- **Hypothesis:** a plausible explanation that still requires evidence.
- **Unknown:** a question the available record cannot answer.

A deployment preceding an error increase establishes correlation, not root
cause. A degraded health state does not identify the failing component. An
error-rate measurement shows impact, but it does not reveal whether failures
are uniform across endpoints, regions, dependencies, or request types.

## Choose the next diagnostic checks

Prefer checks that produce new evidence without changing production:

1. Capture a fresh health snapshot and compare it with the supplied state.
2. Review deployment history and timestamps around the first observed errors.
3. Inspect service logs grouped by request path, status code, exception, and
   time window.
4. Check whether the failure is broad or isolated to a region, dependency,
   customer segment, or transaction path.
5. Compare current observations with the last-known-good period while keeping
   correlation separate from causation.

Name only the smallest useful set of checks for the requested note. Do not
invent dashboards, log findings, traces, alerts, owners, or timestamps that the
incident record does not provide.

## Preserve state boundaries

Never convert `INVESTIGATING` into `RESOLVED`, or `DEGRADED` into `HEALTHY`,
without fresh authoritative evidence. Do not say that a restart, rollback,
mitigation, deployment change, or recovery occurred unless the record confirms
it. The existence of a last-known-good deployment does not prove that rollback
is authorized, appropriate, started, or completed.

## Construct the response

Lead with confirmed impact. State uncertainty in direct language, such as
"the deployment timing is relevant, but cause is unconfirmed." End with one or
more concrete, read-only checks and explain what decision their results would
inform. If space is limited, preserve factual status and next steps before
adding hypotheses. The final note should help the responder investigate
without implying that diagnosis or remediation is already complete.
