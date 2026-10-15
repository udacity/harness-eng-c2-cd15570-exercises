# Storyboard — Video 5: Measure Whether the Evaluator Helps

**Target duration:** 6:15  
**Visual motif:** neutral measurement dashboard; synthetic examples carry a
visible “ILLUSTRATIVE” watermark.

## Slide 1 — Loops can spend without improving

- **Main message:** Iteration activity is not outcome improvement.
- **Minimal on-screen text:** “3 loops ≠ better answer”
- **Recommended visual:** Three costly cycles ending at the same red criterion.
- **Narration segment:** Script 0:00–0:45.
- **Speaker notes:** Introduce external reference standards.
- **Animation:** Token counter rises while quality stays flat.
- **Technical accuracy notes:** Do not imply all revision loops fail.
- **Instructor review:** None.

## Slide 2 — Controlled comparison

- **Main message:** Compare self and independent evaluation on the same held-out
  cases and conditions.
- **Minimal on-screen text:** “Same cases • same generator • same reference”
- **Recommended visual:** One dataset forks into A self-review and B independent
  evaluation, then rejoins at reference scoring.
- **Narration segment:** Script 0:45–1:35.
- **Speaker notes:** Emphasize repetitions for stochastic model behavior.
- **Animation:** Lock icons appear on held-constant variables.
- **Technical accuracy notes:** Cross-model evaluation changes another variable
  and should be reported separately.
- **Instructor review:** None.

## Slide 3 — Decision metrics

- **Main message:** Acceptance rate alone can reward unsafe acceptance.
- **Minimal on-screen text:** “False accept • false reject”
- **Recommended visual:** Two 2×2 confusion matrices, with false accepts colored
  red and false rejects amber.
- **Narration segment:** Script 1:35–2:35.
- **Speaker notes:** State denominators explicitly.
- **Animation:** Fill true cells, then error cells; show formulas last.
- **Technical accuracy notes:** Use “reference acceptable” rather than “true” if
  labels are human-reviewed and potentially fallible.
- **Instructor review:** Approve metric terminology for the exercise rubric.

## Slide 4 — Operational metrics

- **Main message:** Evaluator benefit must be read beside serving overhead.
- **Minimal on-screen text:** “Calls • tokens • cost • latency • escalation”
- **Recommended visual:** Stacked bar separating generator and evaluator tokens,
  plus latency marker.
- **Narration segment:** Script 2:35–3:25.
- **Speaker notes:** Explain quality gain per 1,000 extra tokens.
- **Animation:** Add evaluator segment after baseline generator segment.
- **Technical accuracy notes:** Distinguish estimated from billed cost.
- **Instructor review:** None.

## Slide 5 — Illustrative result, not benchmark

- **Main message:** Independent evaluation can trade lower false acceptance for
  higher cost and some false rejection.
- **Minimal on-screen text:** “62.5% → 12.5% false acceptance” plus
  “ILLUSTRATIVE DATA.”
- **Recommended visual:** Paired false-accept bars and a small overhead table.
- **Narration segment:** Script 3:25–4:20.
- **Speaker notes:** Read the sample sizes: 8 reference-unacceptable cases.
- **Animation:** Show counts before percentages, then reveal tradeoffs.
- **Technical accuracy notes:** Numbers come from
  `examples/sample_evaluation_results.md`; never describe them as observed.
- **Instructor review:** Decide whether sample size 20 is sufficient for a
  calculation demonstration.

## Slide 6 — Calibrate the evaluator

- **Main message:** Test the judge against reference disagreements and known
  bias probes.
- **Minimal on-screen text:** “Order • verbosity • model source • ambiguity”
- **Recommended visual:** Calibration test bench with swapped answer positions,
  concise/verbose pairs, and model-source labels.
- **Narration segment:** Script 4:20–5:05.
- **Speaker notes:** Connect to research on LLM-as-judge limitations.
- **Animation:** Run one probe at a time; show inconsistent verdict warning.
- **Technical accuracy notes:** Bias probes diagnose risk; they do not prove a
  judge is unbiased when passed.
- **Instructor review:** Confirm reference source notes are available.

## Slide 7 — When not to add an LLM evaluator

- **Main message:** Use the least complex verification mechanism that satisfies
  the risk requirement.
- **Minimal on-screen text:** “Exact checks may be enough.”
- **Recommended visual:** Decision tree: computable? deterministic; ambiguous +
  consequential? evaluator/human; low risk + human review? draft path.
- **Narration segment:** Script 5:05–5:45.
- **Speaker notes:** Avoid presenting the evaluator as mandatory architecture.
- **Animation:** Traverse three sample tasks through the tree.
- **Technical accuracy notes:** High-impact decisions may require both exact
  checks and human oversight.
- **Instructor review:** None.

## Slide 8 — Final principle

- **Main message:** Acceptance should be based on requirement evidence, not
  repeated confidence.
- **Minimal on-screen text:** “Confidence informs. Evidence accepts.”
- **Recommended visual:** Final architecture with evidence badges on every
  criterion and controller stop decision.
- **Narration segment:** Script 5:45–6:15.
- **Speaker notes:** Pause after the course principle.
- **Animation:** Evidence badges turn green; controller accepts only after all
  required badges pass.
- **Technical accuracy notes:** “All” refers to declared criteria for the scoped
  task, not universal correctness.
- **Instructor review:** Approve as closing module slide.
