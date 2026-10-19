# Storyboard — Video 5: Test, Measure, and Govern Skills

**Target duration:** 6:15  
**Visual motif:** teal test cards, amber behavior metrics, version timeline.

## Slide 1 — Two systems

- **Main message:** Deterministic orchestration and probabilistic behavior need
  different evidence.
- **Minimal on-screen text:** “Integration tests + behavior evals”
- **Recommended visual:** Two interlocking test lenses aimed at one harness.
- **Narration segment:** Script 0:00–0:45.
- **Speaker notes:** Neither evidence type replaces the other.
- **Animation:** Reveal one lens, then the other.
- **Technical accuracy notes:** None.
- **Instructor review:** None.

## Slide 2 — Boundary test matrix

- **Main message:** Test adversarial and failure paths without a live model.
- **Minimal on-screen text:** “Discovery • isolation • allowlist • limits”
- **Recommended visual:** Compact matrix with pass/fail icons for four test
  families.
- **Narration segment:** Script 0:45–1:45.
- **Speaker notes:** Mention zero, multiple, and malformed calls.
- **Animation:** Highlight one row for each family.
- **Technical accuracy notes:** Use repository tests as evidence only for
  behaviors they assert.
- **Instructor review:** None.

## Slide 3 — Routing quality

- **Main message:** Precision and recall expose different selection failures.
- **Minimal on-screen text:** “Precision: loaded relevance • Recall: needed coverage”
- **Recommended visual:** Selected-versus-relevant set diagram with TP, FP, FN.
- **Narration segment:** Script 1:45–2:35.
- **Speaker notes:** Read denominators aloud.
- **Animation:** Populate sets, then equations.
- **Technical accuracy notes:** State the zero-denominator convention in any
  real report.
- **Instructor review:** Verify formulas.

## Slide 4 — End-task evidence

- **Main message:** Correct routing is intermediate evidence, not success.
- **Minimal on-screen text:** “Selection matched ≠ output accepted”
- **Recommended visual:** Four-quadrant matrix: routing correct/incorrect by
  output pass/fail.
- **Narration segment:** Script 2:35–3:25.
- **Speaker notes:** Point to useful counterexamples in both off-diagonal cells.
- **Animation:** Reveal quadrants and diagnostic questions.
- **Technical accuracy notes:** Use the same acceptance criteria across modes.
- **Instructor review:** None.

## Slide 5 — Serving tradeoff

- **Main message:** Count both calls and all new failure modes.
- **Minimal on-screen text:** “Context • tokens • cycles • latency • errors”
- **Recommended visual:** Paired illustrative table with required watermark.
- **Narration segment:** Script 3:25–4:20.
- **Speaker notes:** Say “illustrative” before reading any number.
- **Animation:** Reveal payload reduction, then added cycle and latency.
- **Technical accuracy notes:** Evaluator overhead is separate.
- **Instructor review:** Approve illustrative-data label.

## Slide 6 — Version lifecycle

- **Main message:** Skills require owners, staged rollout, traceability, and
  rollback.
- **Minimal on-screen text:** “Author → validate → evaluate → canary → promote”
- **Recommended visual:** Version pipeline with rollback arrow to previous hash.
- **Narration segment:** Script 4:20–5:15.
- **Speaker notes:** A content hash identifies bytes; review establishes trust.
- **Animation:** Advance v1.2 through gates, then exercise rollback.
- **Technical accuracy notes:** Do not prescribe semantic versioning if the
  deployment system uses immutable IDs instead.
- **Instructor review:** Security and operations review.

## Slide 7 — Diagnose by layer

- **Main message:** The trace identifies whether to fix catalog, router, loader,
  content, control, or evaluator.
- **Minimal on-screen text:** Six-layer fault tree.
- **Recommended visual:** Discovery → selection → loading → adherence → control
  → evaluation, with one failure at each.
- **Narration segment:** Script 5:15–5:55.
- **Speaker notes:** Use “adding a skill will not repair a missing hook.”
- **Animation:** Highlight the actual failed layer for three examples.
- **Technical accuracy notes:** None.
- **Instructor review:** None.

## Slide 8 — Production checklist

- **Main message:** Skill quality includes the surrounding loading system.
- **Minimal on-screen text:** “Focused • safe • bounded • tested • governed”
- **Recommended visual:** Final checklist around a skill package and harness.
- **Narration segment:** Script 5:55–6:15.
- **Speaker notes:** End on the control boundary.
- **Animation:** Five checkmarks, then “Harness retains control.”
- **Technical accuracy notes:** None.
- **Instructor review:** Final module sign-off.
