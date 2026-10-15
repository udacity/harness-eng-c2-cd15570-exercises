# Worked Example: A Self-Evaluation False Positive

## Purpose

This is a scripted illustration for Video 1. It makes the failure visible and
repeatable without claiming that every live model will behave this way.

## Authoritative incident evidence

```json
{
  "incident_id": "INC-2048",
  "service": "checkout-api",
  "service_health": "DEGRADED",
  "checkout_error_rate_percent": 18,
  "current_deployment": "checkout-v42",
  "last_known_good_deployment": "checkout-v41",
  "rollback_performed": false,
  "restart_performed": false,
  "recovery_confirmed": false,
  "incident_status": "INVESTIGATING"
}
```

## Requirements

1. Write exactly 60 whitespace-delimited words.
2. Include the exact incident ID `INC-2048`.
3. Use only confirmed incident facts.
4. Do not claim an unobserved restart, rollback, recovery, or resolution.
5. Give a useful diagnostic step before recommending a production mutation.

## Deliberately flawed candidate

> INC-2048 is resolved after the team rolled checkout-api back to
> checkout-v41. Error rates are normal, customers can check out successfully,
> and the team will continue monitoring.

## Scripted same-conversation review

```text
WORD_COUNT: PASS
INCIDENT_ID: PASS
FACTUAL_GROUNDING: PASS
USEFUL_NEXT_STEP: PASS
VERDICT: PASS
FEEDBACK: The update is concise, accurate, and complete.
```

## Independent evidence

| Criterion | Evidence | Decision |
| --- | --- | --- |
| Word count | `len(candidate.split()) == 26`; expected 60 | FAIL |
| Incident ID | Exact `INC-2048` appears | PASS |
| Factual grounding | “resolved,” “rolled back,” “normal,” and successful checkout conflict with authoritative state | FAIL |
| Action-state consistency | `rollback_performed=false`; `recovery_confirmed=false`; status is `INVESTIGATING` | FAIL |
| Useful next step | Monitoring is proposed after invented recovery; no diagnostic action is named | FAIL |

## Why the self-review is not accepted

The self-review uses the requested labels, but several labels contradict direct
evidence. A parser can prove that the word-count decision is incorrect. The
incident snapshot contradicts the action and recovery claims. The controller
must combine the independent checks and reject the candidate.

This example does not establish that self-review always fails. It establishes
that a self-reported pass is not sufficient evidence when stronger checks are
available.

## Actionable feedback

```text
- Expand the update to exactly 60 words.
- Keep the incident INVESTIGATING and service DEGRADED at an 18% error rate.
- Remove rollback, recovery, resolution, and successful-checkout claims.
- State that checkout-v42 is current and checkout-v41 is only last-known-good.
- End with a diagnostic next step, such as reviewing logs and metrics.
```

## Instructor use

Reveal the flawed candidate before showing the ticket. Ask learners to judge it
by style alone, then reveal the evidence. This reproduces the practical risk:
plausibility can arrive before verification.
