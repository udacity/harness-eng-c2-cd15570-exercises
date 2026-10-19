# Storyboard — Video 4: Engineer a Reliable Hooked Loop

**Target duration:** 7:00  
**Visual motif:** complete loop trace with explicit state version and evidence
freshness markers.

## Slide 1 — End-to-end chain

- **Main message:** Reliability depends on every stage honoring the boundary.
- **Minimal on-screen text:** “Parse → resolve → check → dispatch → record”
- **Recommended visual:** Chain links with failure markers at each handoff.
- **Narration segment:** Script 0:00–0:45.
- **Speaker notes:** Pure-check success alone is insufficient.
- **Animation:** Build chain, then break one link.
- **Technical accuracy notes:** None.
- **Instructor review:** None.

## Slide 2 — Parse and fail closed

- **Main message:** Malformed or unknown calls never reach policy-light tools.
- **Minimal on-screen text:** “Exact target • exact shape • trusted ID”
- **Recommended visual:** Parser filters invalid JSON, extra keys, wrong ID, and
  unsupported tool.
- **Narration segment:** Script 0:45–1:40.
- **Speaker notes:** Provider schemas reduce but do not replace validation.
- **Animation:** Reject one malformed card at each filter.
- **Technical accuracy notes:** Do not report hook checks as run if parsing
  failed before the hook.
- **Instructor review:** None.

## Slide 3 — Combine and honor

- **Main message:** The dispatcher, not the model, combines required findings.
- **Minimal on-screen text:** “Any FAIL/ERROR → BLOCK”
- **Recommended visual:** Findings table drives a single switch before tool.
- **Narration segment:** Script 1:40–2:35.
- **Speaker notes:** Show zero spy-tool calls on block.
- **Animation:** Flip one check to fail; dispatcher arrow closes.
- **Technical accuracy notes:** Applicability policy must be explicit.
- **Instructor review:** None.

## Slide 4 — Feedback and bounded recovery

- **Main message:** Structured block evidence supports recovery without waiver.
- **Minimal on-screen text:** “Block → explain/retrieve/revise → retry or stop”
- **Recommended visual:** Tool-result card loops to model; cycle budget remains
  visible.
- **Narration segment:** Script 2:35–3:25.
- **Speaker notes:** Repeated invalid proposal is rechecked, never grandfathered.
- **Animation:** One recovery path and one limit-exhaustion path.
- **Technical accuracy notes:** Limit exhaustion is failure/escalation, not
  implicit allow.
- **Instructor review:** None.

## Slide 5 — Replay protection

- **Main message:** Canonical identity and atomic idempotency prevent duplicate
  effects.
- **Minimal on-screen text:** “Same effect, at most once”
- **Recommended visual:** Two equivalent calls map to one signature/idempotency
  record.
- **Narration segment:** Script 3:25–4:15.
- **Speaker notes:** Demo record is in-memory and run-scoped; production often
  needs durable storage.
- **Animation:** First executes and records; second blocks.
- **Technical accuracy notes:** Canonicalization and idempotency scope must match
  business semantics.
- **Instructor review:** None.

## Slide 6 — Evidence invalidation

- **Main message:** Mutations invalidate observations about the previous state.
- **Minimal on-screen text:** “Mutation → health evidence stale”
- **Recommended visual:** Health snapshot version 17 is crossed out after state
  moves to version 18.
- **Narration segment:** Script 4:15–5:00.
- **Speaker notes:** Generalize beyond health.
- **Animation:** Mutation advances version; freshness badge expires.
- **Technical accuracy notes:** Retrieval itself does not guarantee freshness
  unless source and timestamp/version policy are defined.
- **Instructor review:** None.

## Slide 7 — Check/use atomicity

- **Main message:** Shared state may require the invariant and write to be one
  atomic operation.
- **Minimal on-screen text:** “Checked v17 • current v18 → reject”
- **Recommended visual:** Timeline showing concurrent write between hook and
  mutation; compare-and-swap closes the gap.
- **Narration segment:** Script 5:00–5:55.
- **Speaker notes:** Name transaction, lock, expected version, conditional API.
- **Animation:** First show race, then expected-version failure.
- **Technical accuracy notes:** Cite CWE-367 as the general check/use risk.
- **Instructor review:** Security/concurrency review.

## Slide 8 — Honest trace

- **Main message:** Request, decision, execution, and outcome are different
  observability states.
- **Minimal on-screen text:** Trace fields only.
- **Recommended visual:** Event timeline with “not checked” and “not run” badges.
- **Narration segment:** Script 5:55–6:35.
- **Speaker notes:** Contrast basic “not checked” with zero violations.
- **Animation:** Populate events in causal order.
- **Technical accuracy notes:** Do not infer tool success from hook allow.
- **Instructor review:** None.

## Slide 9 — Reliable-loop invariant

- **Main message:** Every protected effect requires current authorization and
  validity evidence.
- **Minimal on-screen text:** Full invariant statement.
- **Recommended visual:** Solid boundary around protected effect.
- **Narration segment:** Script 6:35–7:00.
- **Speaker notes:** Transition to proof and operations.
- **Animation:** Lock closes only after all gates pass.
- **Technical accuracy notes:** Module 4 supplies authorization implementation.
- **Instructor review:** None.
