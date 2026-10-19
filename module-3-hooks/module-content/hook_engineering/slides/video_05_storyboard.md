# Storyboard — Video 5: Test and Operate Deterministic Controls

**Target duration:** 6:15  
**Visual motif:** teal deterministic tests, purple live-model evidence, and a
versioned policy pipeline.

## Slide 1 — Two proofs

- **Main message:** Correct predicates and complete boundary wiring are separate
  obligations.
- **Minimal on-screen text:** “Rule correctness + enforcement coverage”
- **Recommended visual:** Two proof documents join into one reliability claim.
- **Narration segment:** Script 0:00–0:45.
- **Speaker notes:** Use direct-bypass example.
- **Animation:** Show each proof incomplete alone.
- **Technical accuracy notes:** None.
- **Instructor review:** None.

## Slide 2 — Adjacent boundary cases

- **Main message:** Test values immediately on both sides of policy thresholds.
- **Minimal on-screen text:** `$100.00/$100.01 • $500.00/$500.01 • ±$0.01`
- **Recommended visual:** Three number lines plus malformed-value cards.
- **Narration segment:** Script 0:45–1:40.
- **Speaker notes:** Include exact error paths, not only Boolean outcomes.
- **Animation:** Step across each boundary.
- **Technical accuracy notes:** Use the fictional course policy exactly.
- **Instructor review:** Verify formulas and thresholds.

## Slide 3 — Spy the tool

- **Main message:** The decisive test observes the side effect, not only the
  hook return value.
- **Minimal on-screen text:** “BLOCK → calls=0 • ALLOW → calls=1”
- **Recommended visual:** Hook result beside instrumented tool-call counter and
  unchanged/changed state.
- **Narration segment:** Script 1:40–2:35.
- **Speaker notes:** Include call-ID feedback assertion.
- **Animation:** Run block then allow test.
- **Technical accuracy notes:** Exactly-once may require durable idempotency in
  distributed production systems.
- **Instructor review:** None.

## Slide 4 — Sequence properties

- **Main message:** Reliable hooks preserve invariants across multiple cycles.
- **Minimal on-screen text:** “Freshness • replay • transition • unchanged on block”
- **Recommended visual:** Small state machine from investigating to monitoring
  to resolved with forbidden arrows.
- **Narration segment:** Script 2:35–3:20.
- **Speaker notes:** Explain property tests as supplements.
- **Animation:** Attempt forbidden and repeated transitions.
- **Technical accuracy notes:** The course demo does not implement every
  possible status-transition rule.
- **Instructor review:** None.

## Slide 5 — Deterministic versus live evidence

- **Main message:** Offline tests prove code cases; live runs demonstrate model
  interaction with the boundary.
- **Minimal on-screen text:** “No-model tests ≠ live orchestration—and both matter”
- **Recommended visual:** Split test lanes converge on one report.
- **Narration segment:** Script 3:20–4:05.
- **Speaker notes:** A hook not invoked is not a pass.
- **Animation:** Stable hook decision under varied model proposals.
- **Technical accuracy notes:** Keep model time separate from hook time.
- **Instructor review:** None.

## Slide 6 — Reliability dashboard

- **Main message:** Monitor coverage and forbidden execution escapes.
- **Minimal on-screen text:** “proposals • invocations • decisions • executions”
- **Recommended visual:** Funnel with zero-red-line for execution after block.
- **Narration segment:** Script 4:05–4:55.
- **Speaker notes:** Call out invocation-rate drops as possible bypass evidence.
- **Animation:** Align allowed count with execution count; block/error with zero.
- **Technical accuracy notes:** Counts require complete instrumentation.
- **Instructor review:** Operations review.

## Slide 7 — Policy deployment

- **Main message:** Version rules and tests together, then canary and roll back.
- **Minimal on-screen text:** “Review → test → canary → promote → monitor”
- **Recommended visual:** Policy version pipeline with historical-scenario
  replay and rollback arrow.
- **Narration segment:** Script 4:55–5:45.
- **Speaker notes:** Environment thresholds must be recorded as inputs.
- **Animation:** v3.2 moves through gates; regression triggers rollback.
- **Technical accuracy notes:** Version identifier does not prove correctness.
- **Instructor review:** None.

## Slide 8 — Composed reliability

- **Main message:** Hooks enforce known exact invariants within a larger harness.
- **Minimal on-screen text:** “Skills guide • permissions authorize • hooks validate • tools act • evaluators verify”
- **Recommended visual:** Final layered harness architecture.
- **Narration segment:** Script 5:45–6:15.
- **Speaker notes:** End on unavoidable boundaries, not model distrust.
- **Animation:** Assemble components in course order.
- **Technical accuracy notes:** Each component remains fallible and testable.
- **Instructor review:** Final module sign-off.
