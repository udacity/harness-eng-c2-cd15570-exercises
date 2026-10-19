# Chart Specifications

All example values in this file are illustrative. Every rendered chart must
carry the watermark:

```text
ILLUSTRATIVE DATA — NOT A BENCHMARK
```

## C1 — Loaded skill payload by task

**Question:** How much complete skill text did each path supply?

- Chart: grouped horizontal bars.
- Categories: diagnosis, stakeholder update, incident response.
- Series: eager baseline and on-demand.
- Unit: complete skill source characters.
- Annotation: characters are not API tokens or total prompt size.
- Required labels: exact value on every bar and skill names loaded below it.

## C2 — Serving-token composition

**Question:** Which parts contribute to total input tokens?

- Chart: stacked bars.
- Eager segments: base/task, all skill text.
- On-demand segments: base/task, catalog/schema, selection context, selected
  skill results, writing context.
- Unit: API-reported input tokens summed across serving calls.
- Exclusion: evaluator tokens shown in a separate outlined bar.

## C3 — Latency by cycle

**Question:** What latency does routing add?

- Chart: floating stacked bars.
- Eager: writing call.
- On-demand: selection call plus writing call.
- Show median and p95 only when enough repeated runs exist.
- Exclude presenter pauses and label network/model time measurement method.

## C4 — Routing precision and recall

**Question:** Does the router load relevant skills without excessive extras?

- Chart: two bars per task plus overall micro/macro summaries.
- Range: 0–100% with raw TP/FP/FN labels.
- Include a separate no-skill accuracy indicator.
- State the reference labeling process and zero-denominator convention.

## C5 — Routing versus task success

**Question:** Does correct selection translate into accepted output?

- Chart: 2×2 heatmap.
- Rows: expected selection matched / did not match.
- Columns: final output accepted / failed.
- Cell label: run count and two representative failure IDs.
- Interpretation: off-diagonal cells reveal redundant skills, weak content,
  evaluator mismatch, or recovery despite routing error.

## C6 — Version regression timeline

**Question:** Did a skill change improve the intended tasks without regressions?

- Chart: control-style time series across version deployment markers.
- Series: task acceptance, routing recall, mean total serving tokens, loader
  error rate.
- Annotations: canary start, promotion, rollback.
- Do not imply causality without a controlled comparison.

## Data provenance footer

Every measured chart must include:

- repository commit;
- skill versions or content hashes;
- model identifier and settings;
- task set and run count;
- timestamp and environment;
- metric formula;
- missing-data treatment; and
- whether evaluator overhead is included.
