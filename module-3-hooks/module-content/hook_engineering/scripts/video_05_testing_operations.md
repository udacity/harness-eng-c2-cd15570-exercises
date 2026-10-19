# Video 5 — Test and Operate Deterministic Controls

**Target duration:** 6 minutes 15 seconds  
**Learning objective:** Prove hook logic and wiring, monitor safety properties,
and change policies without losing reproducibility.

## Instructor narration

### [Slide 1] Test the predicate and the boundary — 0:00–0:45

There are two things to prove.

First, each antidote returns the correct result for its input domain. Second,
every protected action actually passes through the hook and honors the result.

A hundred unit tests for `check_meal_limit` do not help if one submission path
calls the tool directly. A wiring test without threshold cases can preserve an
incorrect policy. Use both.

### [Slide 2] Exact boundary tests — 0:45–1:40

Translate every comparison into adjacent examples.

For the meal limit, test $100.00 and $100.01. For approval, test $500.00 and
$500.01. For totals, test equality and a one-cent difference. For incident
resolution, test every combination of healthy or degraded and recovery true or
false.

Then test malformed values: Booleans, NaN, infinity, fractions of a cent,
missing keys, extra keys, wrong types, unknown tools, and mismatched IDs.

These cases reveal off-by-one logic and accidental fail-open behavior.

### [Slide 3] Integration and bypass tests — 1:40–2:35

Wrap the protected tool in a spy. On block, assert its call count is zero and
state is unchanged. On allow, assert it executes exactly once. Verify the block
payload returns with the correct call ID and the next cycle receives it.

Exercise every dispatcher, API route, worker, and administrative path that can
produce the effect. Attempt a direct bypass. In a real database integration,
simulate an expected-version conflict between check and write.

The most important assertion is not “the hook returned false.” It is “the
forbidden effect did not occur.”

### [Slide 4] State-machine and property tests — 2:35–3:20

State-machine tests cover sequences rather than isolated calls.

A successful mutation invalidates health evidence. An identical replay cannot
execute twice. `RESOLVED` cannot be reached from a degraded or unconfirmed
state. A blocked call leaves the state version unchanged.

Property tests can cover ranges: every cent-precise meal amount at or below the
limit passes, and every amount above it fails. Reordering JSON keys cannot
change a canonical signature.

Keep a few named examples because they communicate policy clearly during
review.

### [Slide 5] Separate live-model evidence — 3:20–4:05

Deterministic tests require no model and should be fast and repeatable. Live
model runs answer different questions: did the model propose the action, did it
recover after a block, and did the final explanation reflect execution
evidence?

If the model never requests submission, the hook was not exercised. Do not
report a pass. If a live run varies while the same proposed call yields the same
hook result, the deterministic boundary is working as designed.

Keep model tokens and latency separate from hook execution time.

### [Slide 6] Measure safety invariants — 4:05–4:55

Count protected proposals, hook invocations, decisions by rule, hook errors,
and protected tool executions. The critical comparison is executions after
block or error; that number must remain zero.

Monitor repeated executions, stale-state conflicts, policy-version coverage,
and recovery after blocks. A sudden drop in hook invocations while tool
executions stay level is a possible bypass or instrumentation regression.

Alert on integrity properties, not only average latency.

### [Slide 7] Version and deploy policy — 4:55–5:45

Treat hooks as production policy code. Assign an owner, review changes, record a
policy version and code revision, run deterministic suites, canary changes, and
retain rollback.

When a threshold changes, deploy the code and tests together. Trace the version
used for every decision. Re-evaluate historical scenarios against the new
policy before promotion and document intended decision changes.

Avoid silently changing environment variables that affect thresholds without
capturing their values as versioned decision inputs.

### [Slide 8] Reliability with honest limits — 5:45–6:15

Hooks make agent loops more reliable by turning known, computable failure modes
into enforced, testable boundaries. They are especially valuable around side
effects, state transitions, budgets, replay, and exact policy.

They do not replace skills, permissions, tools, evaluators, transactions, or
human judgment. Reliability comes from composing those components with clear
responsibilities and preserving evidence at every boundary.

## Demonstration cue

Run the deterministic expense suite, then the incident comparison:

```bash
cd module-3-hooks/solution
python3 -m unittest test_hooks.py

cd ../demo
python3 main.py compare --scenario unsafe_remediation
```

Narrate the observed model calls. The deterministic tests establish rule
behavior; the live run demonstrates orchestration.

## Closing line

> A reliable harness does not ask the model to remember every safety rule. It
> makes known invariants unavoidable at the boundary where they matter.
