# Chart Specifications

Every chart in this package uses illustrative data from
`examples/sample_evaluation_results.md`. Add a persistent **ILLUSTRATIVE — NOT
BENCHMARK DATA** label to the chart area.

## Chart 1 — False acceptance comparison

**Purpose:** Show that acceptance rate and false acceptance are different.

- **Type:** paired vertical bars
- **X-axis:** Self-evaluation; Independent evaluation
- **Y-axis:** False acceptance rate, 0–70%
- **Values:** 62.5%; 12.5%
- **Direct labels:** `5 of 8`; `1 of 8`
- **Color:** red for both bars; use darker red for larger rate rather than green
  for the smaller bar, because neither error rate is inherently “safe.”
- **Annotation:** “Reference-unacceptable cases: n=8”
- **Alt text:** “Illustrative false acceptance falls from five of eight bad
  cases under self-evaluation to one of eight under independent evaluation.”

## Chart 2 — Error tradeoff

**Purpose:** Prevent one-sided claims by showing false rejection alongside
false acceptance.

- **Type:** grouped dot plot
- **Rows:** False acceptance; false rejection
- **Columns:** rate, 0–70%
- **Series:** self-evaluation and independent evaluation
- **Values:**
  - false acceptance: 62.5%, 12.5%;
  - false rejection: 8.3%, 16.7%.
- **Count labels:** `5/8`, `1/8`, `1/12`, `2/12`
- **Accessibility:** shapes differ by series; do not rely on color.
- **Alt text:** “Illustrative independent evaluation reduces false acceptance
  but increases false rejection from one to two of twelve acceptable cases.”

## Chart 3 — Initial and final quality

**Purpose:** Compare improvement rather than only final scores.

- **Type:** slope chart
- **Scale:** rubric mean, 1–5
- **Self path:** 3.1 initial to 3.7 final
- **Independent path:** 3.1 initial to 4.2 final
- **Annotation:** “Same illustrative initial mean; reference-reviewed final
  score.”
- **Caution:** Do not plot uncertainty bands unless repeated measurements and
  dispersion are actually available.
- **Alt text:** “Both illustrative paths improve from 3.1; self-evaluation ends
  at 3.7 and independent evaluation at 4.2.”

## Chart 4 — Token composition

**Purpose:** Make evaluator overhead visible.

- **Type:** stacked horizontal bars
- **Self path:** 1,500 generator/revision tokens + 500 evaluator tokens
- **Independent path:** 1,650 generator/revision tokens + 1,100 evaluator
  tokens
- **Labels:** total 2,000; total 2,750
- **Do not include:** blind judge or reference-labeling tokens unless the chart
  title explicitly says benchmark overhead.
- **Alt text:** “Illustrative independent evaluation uses 750 more total tokens,
  with the difference concentrated in evaluator work.”

## Chart 5 — Attempt-by-criterion heatmap

**Purpose:** Show fixes and regressions within one run.

- **Columns:** Word count, Incident ID, Format, Grounding, Next step
- **Rows:** Attempt 1, Attempt 2, Attempt 3
- **Cell values:** PASS, FAIL, NOT RUN, or ERROR
- **Overlay:** icon plus text abbreviation; color is secondary.
- **Example pattern:**
  - Attempt 1: FAIL, PASS, PASS, FAIL, PASS
  - Attempt 2: PASS, PASS, PASS, FAIL, PASS
  - Attempt 3: PASS, PASS, PASS, FAIL, PASS
- **Callout:** “Limit reached; grounding unresolved; accepted=false.”

## Chart production rules

1. Display raw counts whenever showing a rate from fewer than 100 examples.
2. Keep denominators visible.
3. Label synthetic, test-fixture, and observed model data distinctly.
4. Never truncate rate axes in a way that exaggerates small differences.
5. Include model, prompt version, sample size, repetitions, and date on real
   experimental charts.
6. Use patterns or shapes in addition to color.
