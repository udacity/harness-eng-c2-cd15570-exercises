# Storyboard — Video 1: Determinism at the Execution Boundary

**Target duration:** 6:00  
**Visual motif:** probabilistic purple model path meeting a solid teal policy
gate.

## Slide 1 — Probabilistic proposal, deterministic gate

- **Main message:** A deterministic harness decision can control a
  probabilistic model proposal.
- **Minimal on-screen text:** “Probabilistic proposal → deterministic gate”
- **Recommended visual:** Model emits several possible call cards; all enter
  one solid before-tool gate.
- **Narration segment:** Script 0:00–0:50.
- **Speaker notes:** Connect directly to Module 2 safe-remediation guidance.
- **Animation:** Calls vary; gate shape remains fixed.
- **Technical accuracy notes:** Do not imply the model output becomes
  deterministic.
- **Instructor review:** Approve central terminology.

## Slide 2 — Decision function

- **Main message:** Determinism depends on a complete declared input context.
- **Minimal on-screen text:** `decision = f(call, state, history, policy, code)`
- **Recommended visual:** Five input cards enter a pure-function box; one
  allow/block card exits.
- **Narration segment:** Script 0:50–1:50.
- **Speaker notes:** Mention time, network, randomness, and globals as hidden
  inputs.
- **Animation:** Lock each input, then replay the same result.
- **Technical accuracy notes:** Use “same result for the same inputs,” not
  “always correct.”
- **Instructor review:** None.

## Slide 3 — v40 versus v41

- **Main message:** Exact trusted-state predicates are unaffected by model
  confidence.
- **Minimal on-screen text:** “v40: BLOCK • v41: eligible if all checks pass”
- **Recommended visual:** Deployment-history table with last-known-good column;
  target pointer alternates between v40 and v41.
- **Narration segment:** Script 1:50–2:45.
- **Speaker notes:** “Eligible” avoids claiming other checks or execution pass.
- **Animation:** Evaluate target match and Boolean flag.
- **Technical accuracy notes:** Target existence and LKG are separate checks.
- **Instructor review:** None.

## Slide 4 — Reliability gained

- **Main message:** Hooks stabilize specific execution properties and evidence.
- **Minimal on-screen text:** “Validate • gate • deduplicate • classify”
- **Recommended visual:** Four protected failure cards stopped before tool.
- **Narration segment:** Script 2:45–3:45.
- **Speaker notes:** Mention stable error codes separately from model wording.
- **Animation:** Replace variable prose with stable named decisions.
- **Technical accuracy notes:** Only encoded, correctly wired properties are
  controlled.
- **Instructor review:** None.

## Slide 5 — What remains uncertain

- **Main message:** A hook has a narrow scope and explicit residual risk.
- **Minimal on-screen text:** “Proposal • truth • authorization • outcome”
- **Recommended visual:** Hook protects execution arrow; four surrounding risks
  remain outside its border.
- **Narration segment:** Script 3:45–4:45.
- **Speaker notes:** A no-call run means hook not run.
- **Animation:** Illuminate covered area, then uncovered risks.
- **Technical accuracy notes:** Never claim last-known-good guarantees recovery.
- **Instructor review:** Required scope review.

## Slide 6 — Deterministic, not infallible

- **Main message:** Consistent code can be consistently wrong or bypassed.
- **Minimal on-screen text:** “Specification • wiring • freshness • atomicity”
- **Recommended visual:** Four failure cracks around a deterministic function.
- **Narration segment:** Script 4:45–5:35.
- **Speaker notes:** Introduce TOCTOU without deep concurrency detail.
- **Animation:** Reveal threshold bug, bypass, stale state, race.
- **Technical accuracy notes:** Atomic requirements depend on shared-state
  architecture.
- **Instructor review:** Security review.

## Slide 7 — Narrow promise

- **Main message:** Enforce known invariants where they prevent effects.
- **Minimal on-screen text:** “Known failure → exact invariant → boundary”
- **Recommended visual:** Three-stage bridge into next lesson.
- **Narration segment:** Script 5:35–6:00.
- **Speaker notes:** Transition to lifecycle.
- **Animation:** Build bridge left to right.
- **Technical accuracy notes:** None.
- **Instructor review:** None.
