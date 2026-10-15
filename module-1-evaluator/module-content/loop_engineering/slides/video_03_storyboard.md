# Storyboard — Video 3: Deterministic and Inferential Criteria

**Target duration:** 6:30  
**Visual motif:** blue exact-check layer followed by orange judgment layer.

## Slide 1 — Replace “good” with observable requirements

- **Main message:** Evaluation quality begins with the definition of success.
- **Minimal on-screen text:** “Good” → five observable conditions
- **Recommended visual:** A vague speech bubble transforms into five checklist
  rows for word count, ID, format, grounding, and next step.
- **Narration segment:** Script 0:00–0:50.
- **Speaker notes:** Read the precise replacement requirement once.
- **Animation:** Blur “good,” then sharpen each measurable condition.
- **Technical accuracy notes:** Requirements must be available before judging;
  do not let the candidate define its own rubric.
- **Instructor review:** Confirm whether one-paragraph format should remain in
  the teaching rubric even though the current demo checks four criteria.

## Slide 2 — Deterministic checks

- **Main message:** Compute exact properties instead of asking a model to
  estimate them.
- **Minimal on-screen text:** `len(split()) == 60`; `"INC-2048" in text`
- **Recommended visual:** Two Python check cards producing explicit PASS/FAIL.
- **Narration segment:** Script 0:50–1:45.
- **Speaker notes:** Explain that the word-count convention is product-defined.
- **Animation:** Candidate flows through both functions; numerical evidence
  appears under each result.
- **Technical accuracy notes:** Substring presence is the current demo rule; a
  stricter product might parse an exact identifier token.
- **Instructor review:** None.

## Slide 3 — Inferential checks

- **Main message:** Semantic judgment still needs precise criteria and supplied
  evidence.
- **Minimal on-screen text:** “Grounded?” “Useful and safe?”
- **Recommended visual:** Evaluator comparing candidate claim cards with the
  authoritative incident snapshot.
- **Narration segment:** Script 1:45–2:40.
- **Speaker notes:** Contrast “Does this look accurate?” with the stated
  grounding rule.
- **Animation:** Connect each candidate claim to supporting or conflicting
  evidence.
- **Technical accuracy notes:** Inferential decisions are probabilistic and
  require calibration.
- **Instructor review:** None.

## Slide 4 — Five-criterion rubric

- **Main message:** Every criterion has a type and explicit pass condition.
- **Minimal on-screen text:** The five-row rubric table.
- **Recommended visual:** Compact matrix using blue badges for deterministic
  and orange badges for inferential.
- **Narration segment:** Script 2:40–3:40.
- **Speaker notes:** Use action-state consistency as an optional sixth example.
- **Animation:** Reveal exact criteria first, then inferential criteria.
- **Technical accuracy notes:** Do not combine criterion failures into one
  opaque score on this slide.
- **Instructor review:** Approve rubric for exercise reuse.

## Slide 5 — Cheap checks before expensive checks

- **Main message:** Layer evaluation so obvious exact failures can bypass model
  cost.
- **Minimal on-screen text:** “Exact gate → semantic review”
- **Recommended visual:** Funnel with an early fail exit and token-cost meter.
- **Narration segment:** Script 3:40–4:35.
- **Speaker notes:** State that batching tradeoffs should be measured.
- **Animation:** Invalid JSON exits left; eligible candidate proceeds to model.
- **Technical accuracy notes:** Avoid claiming deterministic checks are always
  free or sufficient.
- **Instructor review:** None.

## Slide 6 — The split transfers across domains

- **Main message:** Verification mechanism follows criterion type, not business
  domain.
- **Minimal on-screen text:** Coding • SEO • Marketing • CI/CD • Research
- **Recommended visual:** Five domain rows with one blue exact icon and one
  orange judgment icon each.
- **Narration segment:** Script 4:35–5:35.
- **Speaker notes:** Move quickly; choose examples relevant to the audience.
- **Animation:** Reveal one domain per beat.
- **Technical accuracy notes:** Source relevance is not deterministic merely
  because citations exist.
- **Instructor review:** Consider moving unused domains to speaker notes.

## Slide 7 — Evaluate the evaluator

- **Main message:** Independent model findings remain fallible evidence.
- **Minimal on-screen text:** “Parse • preserve • calibrate • audit”
- **Recommended visual:** Evaluator output entering a calibration bench with
  reference labels and disagreement samples.
- **Narration segment:** Script 5:35–6:15.
- **Speaker notes:** Name position and verbosity bias as documented examples,
  not exhaustive categories.
- **Animation:** Add one safeguard at a time.
- **Technical accuracy notes:** Never label an LLM judge as ground truth.
- **Instructor review:** Ensure research citations appear in notes or course
  references.

## Slide 8 — Next: connect the loop

- **Main message:** Criteria need bounded orchestration to improve candidates.
- **Minimal on-screen text:** “Findings → revision → re-check”
- **Recommended visual:** Three nodes from the next lesson's loop, with the
  remainder faded.
- **Narration segment:** Script 6:15–6:30.
- **Speaker notes:** None.
- **Animation:** Pulse the three nodes.
- **Technical accuracy notes:** None.
- **Instructor review:** None.
