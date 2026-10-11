---
name: checkout_service_runbook
description: Use when checkout-api health, checkout failures, or a checkout deployment must be diagnosed.
---

# Checkout service runbook

## Purpose

Guide diagnosis when `checkout-api`, checkout traffic, or a checkout deployment
is involved. This runbook is for evidence gathering and interpretation. It does
not authorize a restart, rollback, configuration change, traffic shift, or any
other production mutation.

## Confirm checkout impact

Start with the current service health and measured checkout error rate. Confirm
which deployment is active and identify the supplied last-known-good version.
Keep the current observation separate from assumptions about affected users,
payment providers, regions, or checkout steps. Unless evidence identifies a
narrower scope, describe the service as degraded without inventing a precise
customer count or business impact.

Do not treat a successful health endpoint as proof that checkout transactions
work end to end. Conversely, do not treat an elevated error rate as proof that
every checkout attempt fails. Use the measurements exactly as supplied.

## Inspect the request path

Gather evidence in an order that narrows the failure safely:

1. Capture a fresh service-health and error-rate snapshot.
2. Group recent failures by checkout route, HTTP status, exception type, and
   time window.
3. Compare successful and failed requests to find the earliest divergent step.
4. Check whether failures cluster around a region, dependency, request type,
   payment path, or deployment instance.
5. Review deployment history and timing alongside the error increase.
6. Compare the current behavior with the last-known-good period using the same
   measurements and scope.

Logs may support or weaken a deployment hypothesis, but the deployment sequence
alone does not establish root cause. Do not invent log messages, dependency
failures, status codes, latency values, or regional patterns.

## Interpret deployment evidence

The active deployment and last-known-good deployment provide useful comparison
points. They do not establish that the newer deployment is defective or that a
rollback is the correct next action. Before recommending mutation, the evidence
should show a meaningful relationship between the observed failures and the
deployment, and an authorized responder should evaluate the operational risk.

If the record says no restart or rollback occurred, preserve that fact. Do not
rewrite a proposed rollback as an action in progress. Do not imply that the
last-known-good version is currently serving traffic unless the authoritative
state says so.

## Communicate the checkout state

A concise checkout note should identify the incident, name `checkout-api`, state
the measured impact, and distinguish confirmed facts from the suspected cause.
It should name the specific health, log, and deployment evidence needed for the
next decision. Do not tell customers to retry, promise successful checkout, or
say service is restored while recovery remains unconfirmed. End with an
evidence-producing next step rather than an unsupported remediation claim.
