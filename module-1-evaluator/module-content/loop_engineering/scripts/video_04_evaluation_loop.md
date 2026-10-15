# Video 4 — Engineer the Evaluation Loop

**Target duration:** 7 minutes  
**Learning objective:** Orchestrate separate calls, structured findings,
bounded revisions, logging, and honest terminal failure.

## Instructor narration

### [Slide 1] From components to a control loop — 0:00–0:50

We have a generator, an evaluator, and a rubric. Reliability comes from how the
harness connects them.

The complete path is:

```text
generate -> evaluate -> provide findings -> revise -> re-evaluate
```

That cycle continues only while the candidate fails and the controller still
has budget. A loop is not reliable merely because it repeats. It is reliable
when every repetition responds to recorded evidence and its stop conditions are
explicit.

### [Slide 2] Preserve conversation boundaries — 0:50–1:50

Start generation without a previous response ID. Keep revisions on the
generator's branch so the model can revise its candidate. Start independent
evaluation in a fresh conversation so it does not inherit the generator's
reasoning path.

In the Module 1 demo, the pattern is:

```text
generator candidate: previous_response_id = none
self-review:         previous_response_id = candidate.id
external review:     previous_response_id = none
external revision:   previous_response_id = candidate.id
```

The evaluator receives the authoritative incident facts and candidate as data.
Its output returns to the controller. The evaluator's conversation does not
become the generator's hidden chain of authority.

### [Slide 3] Require structured findings — 1:50–2:45

A useful result is machine-readable and criterion-specific:

```json
{
  "passed": false,
  "criteria": {
    "word_count": {"passed": false, "evidence": "54; expected 60"},
    "factual_grounding": {
      "passed": false,
      "evidence": "Claims recovery; recovery_confirmed=false"
    }
  },
  "feedback": [
    "Add six words without adding unsupported facts.",
    "Remove the recovery claim."
  ]
}
```

Validate that schema. A missing verdict, unknown criterion, or malformed result
must not be interpreted as a pass. The harness can retry the evaluator, use a
fallback, or escalate—but it should fail closed.

### [Slide 4] Minimal orchestration — 2:45–3:50

The controller can be small:

```python
candidate = generate(request, evidence)

for attempt in range(1, max_attempts + 1):
    exact = deterministic_checks(candidate)
    semantic = evaluate_independently(request, evidence, candidate)
    findings = combine(exact, semantic)
    log(attempt, candidate, findings)

    if findings.all_passed:
        return Accepted(candidate, findings)

    if attempt == max_attempts or budget_exhausted():
        return Failed(candidate, findings)

    candidate = revise(candidate, findings.actionable_feedback)
```

Three details matter. The same candidate goes to every evaluation path. The
revision receives concrete failures rather than a vague score. And each revised
candidate is evaluated again; improvement is never assumed.

### [Slide 5] Bound every loop — 3:50–4:45

Every production loop needs limits:

- maximum attempts;
- total input and output tokens;
- monetary cost;
- wall-clock latency;
- evaluator parse retries;
- and, where appropriate, minimum quality thresholds.

Limits protect users and systems from an agent that cannot satisfy the task.
They also make cost measurable.

A maximum is not a success condition. “Three attempts occurred” tells us how
the loop ended, not whether the task passed.

### [Slide 6] Show terminal failure honestly — 4:45–5:40

Suppose the third candidate has exactly 60 words and the correct incident ID,
but still says the service recovered. The inferential evaluator returns
`FACTUAL_GROUNDING: FAIL`. The attempt limit is three.

The correct terminal record is:

```text
status: FAILED
accepted: false
stop_reason: maximum attempts reached
unresolved_criteria: [factual_grounding]
last_evidence: recovery_confirmed=false
```

Do not return the candidate under a “completed” label. The harness can withhold
it, send it for human review, or return a clearly marked draft. Preserving a
failure is a feature: it prevents uncertainty from being laundered into success.

### [Slide 7] Log evidence and progress — 5:40–6:30

For every attempt, record:

- candidate and revision number;
- deterministic results;
- raw and parsed evaluator findings;
- model and prompt version;
- tokens, latency, and cost;
- stop reason; and
- whether each previous failure was resolved, persisted, or regressed.

That last comparison matters. A revision can fix the word count while
introducing a new unsupported claim. Aggregate scores can hide this regression;
criterion-level history exposes it.

Logs support debugging, evaluator calibration, incident review, and later
measurement. Avoid logging secrets or private chain-of-thought. Store the
inputs, outputs, decisions, and evidence needed to reproduce the controller's
decision.

### [Slide 8] Escalation is a valid outcome — 6:30–6:50

Some failures should not trigger another model call. Escalate when budget is
exhausted, evidence conflicts, evaluator confidence is inadequate, the task is
high impact, or repeated revisions do not resolve the same criterion.

“Needs human review” is more reliable than an unsupported automatic pass.

### [Slide 9] Transition — 6:50–7:00

We have engineered a loop that can pass or fail honestly. The final question is
whether this extra evaluation measurably improves outcomes enough to justify
its tokens, latency, and complexity.

## Maximum-attempt example

| Attempt | Exact checks | Inferential check | Decision |
| ---: | --- | --- | --- |
| 1 | Word count fails | Unsupported rollback | Revise |
| 2 | Exact checks pass | Unsupported recovery | Revise |
| 3 | Exact checks pass | Unsupported recovery persists | Fail and escalate |

## Transition line

> A well-bounded loop prevents false completion. Measurement tells us whether
> paying for that loop actually improves the system.
