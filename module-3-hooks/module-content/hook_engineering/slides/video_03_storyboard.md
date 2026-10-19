# Storyboard — Video 3: Turn Failures into Deterministic Antidotes

**Target duration:** 6:30  
**Visual motif:** red failure cards transformed into teal invariant cards.

## Slide 1 — Antidote definition

- **Main message:** An antidote is a narrow deterministic defense against a
  known failure.
- **Minimal on-screen text:** “Known failure → exact defense”
- **Recommended visual:** $185 meal failure turns into `$amount <= 100.00`.
- **Narration segment:** Script 0:00–0:50.
- **Speaker notes:** State that this is course language, not an API object.
- **Animation:** Transform vague “be safe” into predicate.
- **Technical accuracy notes:** None.
- **Instructor review:** Approve definition.

## Slide 2 — Six-step derivation

- **Main message:** Failures become controls through a repeatable design method.
- **Minimal on-screen text:** “Failure • invariant • boundary • inputs • predicate • evidence”
- **Recommended visual:** Six-step conveyor using premature resolution.
- **Narration segment:** Script 0:50–1:45.
- **Speaker notes:** Read the final two-condition invariant aloud.
- **Animation:** Add one design artifact per step.
- **Technical accuracy notes:** Health and recovery are conjunctive.
- **Instructor review:** None.

## Slide 3 — Trusted inputs

- **Main message:** The harness supplies approval evidence independently of the
  model proposal.
- **Minimal on-screen text:** “Proposal from model • evidence from system”
- **Recommended visual:** Two source lanes enter a check; model lane cannot feed
  trusted-state port.
- **Narration segment:** Script 1:45–2:45.
- **Speaker notes:** Include original expense report and canonical signature.
- **Animation:** Reject a model-supplied approval flag.
- **Technical accuracy notes:** Trusted does not mean infallible; provenance and
  freshness remain required.
- **Instructor review:** None.

## Slide 4 — Thresholds and exact money

- **Main message:** Edge semantics determine policy correctness.
- **Minimal on-screen text:** `$100.00 PASS | $100.01 FAIL`
- **Recommended visual:** Two number lines for meal and approval thresholds plus
  a one-cent total mismatch.
- **Narration segment:** Script 2:45–3:40.
- **Speaker notes:** Explain `>` versus `>=`; mention `Decimal`.
- **Animation:** Step one cent across each boundary.
- **Technical accuracy notes:** Approval threshold rule is “over $500,” not “at
  least $500.”
- **Instructor review:** Verify expense-policy wording.

## Slide 5 — Compose findings

- **Main message:** Small independent checks combine into one fail-closed
  decision.
- **Minimal on-screen text:** “All applicable checks must pass.”
- **Recommended visual:** Five antidote cards feed `HookResult` with four-state
  labels.
- **Narration segment:** Script 3:40–4:35.
- **Speaker notes:** Note demo Boolean limitation for non-applicable rules.
- **Animation:** Accumulate all violations before decision.
- **Technical accuracy notes:** Malformed-shape validation may block before
  individual checks run.
- **Instructor review:** Approve not-applicable nuance.

## Slide 6 — Computable versus judgmental

- **Main message:** Deterministic hooks require explicit facts and boundaries.
- **Minimal on-screen text:** “Unique? computable • Reasonable? underspecified”
- **Recommended visual:** Two-column classification table.
- **Narration segment:** Script 4:35–5:25.
- **Speaker notes:** A rate table could turn part of “reasonable” into a rule.
- **Animation:** Move criteria as specification becomes exact.
- **Technical accuracy notes:** Inferential review must not waive exact checks.
- **Instructor review:** None.

## Slide 7 — Residual-risk card

- **Main message:** Every antidote states what it does not prove.
- **Minimal on-screen text:** “Proves • assumes • does not cover”
- **Recommended visual:** Three-field card for last-known-good antidote.
- **Narration segment:** Script 5:25–6:10.
- **Speaker notes:** Include authorization and outcome as uncovered.
- **Animation:** Fill each field.
- **Technical accuracy notes:** None.
- **Instructor review:** Required safety review.

## Slide 8 — Integration transition

- **Main message:** A predicate needs correctly wired and current execution.
- **Minimal on-screen text:** “Check + honor + current state”
- **Recommended visual:** Predicate card approaches dispatcher and state store.
- **Narration segment:** Script 6:10–6:30.
- **Speaker notes:** Preview TOCTOU.
- **Animation:** Reveal gap between check and write.
- **Technical accuracy notes:** None.
- **Instructor review:** None.
