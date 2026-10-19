# Video 4 — Engineer a Reliable Hooked Loop

**Target duration:** 7 minutes  
**Learning objective:** Integrate hooks with trusted state, tool results,
retries, evidence freshness, replay protection, and atomic execution.

## Instructor narration

### [Slide 1] Reliability is an end-to-end property — 0:00–0:45

A correct check is only one link in the chain. The loop must parse the proposal,
resolve trusted state, call the hook, honor its decision, dispatch at most once,
record the result, update evidence, and continue correctly.

If any link bypasses or reverses that order, the invariant can fail even though
the check function passes every unit test.

### [Slide 2] Parse and fail closed — 0:45–1:40

Start by parsing JSON and requiring an object. Match the tool against a
supported dispatcher. Require the exact key set and correct value types. Match
the incident ID to trusted state.

Malformed input never reaches the business tool. Unknown hook targets block.
If a policy dependency is unavailable or a check raises, use a controlled
error and fail closed for the protected action.

Schema-constrained function calling reduces malformed proposals, but the
application still validates at its trust boundary.

### [Slide 3] Run and combine antidotes — 1:40–2:35

Pass the canonical proposal and one trusted-state snapshot to the antidotes.
Run every applicable check, collect named statuses and all safe violation
messages, and compute one decision.

Do not let the model choose which required checks run. Do not accept because
three of five passed. The combination rule is code: every required applicable
check must pass.

If the result is block, return before the dispatcher. A test spy should prove
the mutation function's call count remains zero.

### [Slide 4] Return evidence and continue — 2:35–3:25

The blocked result is a normal function-call output with the original call ID.
It says `tool_executed=false` and provides named findings.

The model can now explain that v40 was rejected, retrieve new evidence, or
propose v41. If it repeats the same invalid request, the hook evaluates again;
repetition never bypasses the gate.

Bound the loop. A persistent retry should reach a declared maximum and fail or
escalate, not run forever and not eventually waive the rule.

### [Slide 5] Prevent replay and repeated effects — 3:25–4:15

Retries are dangerous around side effects. The incident demo creates a
canonical signature from tool name and sorted JSON arguments, and records it
after successful execution. The repeated-mutation antidote blocks the same
signature later in the run.

Production systems often need durable idempotency keys beyond one process. The
tool or data store should atomically record the key with the effect so a retry,
restart, or duplicate delivery cannot perform it twice.

Canonicalization must be defined carefully; semantically equivalent requests
should not evade deduplication through key order or harmless formatting.

### [Slide 6] Invalidate stale evidence — 4:15–5:00

Fresh health evidence is valid only for the state it describes. After a
mutation executes, the demo sets `health_checked` back to false. A later
mutation requires another service-health retrieval.

This prevents the loop from reusing a pre-change snapshot as proof for a
post-change decision.

Generalize the pattern: every side effect should declare which cached evidence,
plans, permissions, or derived values it invalidates. Reliability requires
state-aware evidence, not just more tool calls.

### [Slide 7] Close the check/use gap — 5:00–5:55

The demo uses one in-memory process and disables parallel tool calls, so the
sequence is easy to inspect. Real state may change between validation and
mutation.

If the hook checks database version 17 and another actor writes version 18
before the tool executes, the old decision may no longer be valid. Reduce that
time-of-check/time-of-use gap with a transaction, lock, compare-and-swap,
expected-version precondition, or business API that performs the invariant and
write atomically.

A before-tool hook is the orchestration boundary. The storage boundary may
still need enforcement.

### [Slide 8] Observe each state separately — 5:55–6:35

Trace `requested`, `parsed`, `authorized`, `hook_executed`, each check,
`allowed` or `blocked`, `tool_executed`, postcondition, and final response.

Basic mode says violations were not checked, not zero. If the model never
requests a mutation, hooks are not run, not passed. If the hook allows but the
tool fails, do not label the mutation completed.

These distinctions turn logs into evidence instead of a success story.

### [Slide 9] Reliable loop invariant — 6:35–7:00

The reliable loop invariant is:

> No protected effect occurs unless authorization and every required current
> invariant pass at the execution boundary.

Next, we will test that claim across predicates, thresholds, integration paths,
retries, and policy changes.

## Demonstration cue

Trace `_tool_result()` in `demo/agent.py`. Highlight `parallel_tool_calls=False`,
the early return on block, signature recording after execution, freshness
invalidation, and `MAX_CYCLES`.

## Transition line

> Deterministic code makes the claim testable. Coverage and operations decide
> whether the claim remains true in the system.
