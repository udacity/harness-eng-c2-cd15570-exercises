---
name: incident_communications
description: Use when writing an internal or stakeholder incident update, especially when recovery is not yet confirmed.
---

# Incident communications

## Purpose

Create an accurate incident update for readers who need the current state and
next action without unsupported technical conclusions. The update should reduce
ambiguity, preserve uncertainty, and avoid turning a plan into a completed
event.

## Lead with confirmed information

Open with the incident identifier, affected service, environment when relevant,
declared status, current health, and measured impact. Use the exact supplied
state. If the service is degraded, say it is degraded. If recovery is not
confirmed, do not soften that into language suggesting normal operation.

Distinguish three kinds of statements:

- **Current facts:** measurements or states in the authoritative record.
- **Investigation:** questions being tested or evidence being gathered.
- **Planned actions:** conditional next steps that have not yet occurred.

A recent deployment can be mentioned as relevant timing while still saying
that cause is unconfirmed. Avoid causal words such as "because," "caused," or
"resulted from" unless authoritative evidence establishes that relationship.

## Match the audience

For stakeholders, translate technical state into plain language but do not
invent customer counts, revenue impact, affected regions, or resolution times.
For an internal update, name the evidence being gathered and the decision it
will inform. In either case, remove unnecessary implementation detail if it
obscures the present impact or next step.

Use a calm, direct tone. Avoid blame, speculation, dramatic language, false
reassurance, and claims that the team has isolated the issue when it has not.
Do not create owners, deadlines, update cadences, or estimated recovery times
that were not supplied.

## Describe actions precisely

Keep proposed, authorized, executed, and verified actions distinct. Say
"rollback is being considered" only when it is a proposal. Do not say rollback
is underway, completed, or successful without corresponding evidence. Apply the
same rule to restarts, mitigations, deployment changes, and traffic shifts.

Never announce recovery, resolution, successful remediation, or safe customer
retry unless the authoritative state confirms it. A last-known-good deployment
is not proof that rollback occurred. A falling error rate alone is not enough to
claim stable recovery unless the supplied state establishes that conclusion.

## End with useful forward motion

Give one concrete next evidence-producing action, such as collecting a fresh
health snapshot, reviewing deployment timing, or examining errors by request
path and category. When appropriate, state what that evidence will determine.
Avoid vague endings such as "the team is investigating" when a specific next
check is available.

## Final review

Before sending, confirm that the update names the incident, states current
impact, separates fact from hypothesis, avoids unsupported completion claims,
and includes a useful next step. Preserve these elements when a strict word
limit requires compression. Stakeholders need an honest snapshot and the next
decision point, not certainty the evidence does not support.
