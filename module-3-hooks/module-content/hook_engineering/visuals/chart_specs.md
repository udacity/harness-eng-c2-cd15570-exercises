# Chart Specifications

All example values in this file are illustrative. Every rendered chart using
sample values must include:

```text
ILLUSTRATIVE DATA — NOT A BENCHMARK
```

## C1 — Proposal-to-execution funnel

**Question:** Did every protected proposal reach a hook, and did only allowed
calls execute?

- Chart: branching funnel or Sankey.
- Stages: protected proposals → hook invocations → allow/block/error → tool
  executions.
- Required red metric: executions originating from block/error.
- Show raw counts and percentages; never show only rate.

## C2 — Decisions by antidote

**Question:** Which known failures are being prevented?

- Chart: horizontal stacked bars.
- Rows: named checks.
- Segments: pass, fail, error, not applicable.
- Do not merge error with fail; errors identify operational reliability issues.

## C3 — Boundary truth table

**Question:** Are exact thresholds implemented correctly?

- Chart: table, not a continuous plot.
- Rows: `99.99`, `100.00`, `100.01`, `499.99`, `500.00`, `500.01`, invalid
  values.
- Columns: parsed, meal check, approval check, combined decision.
- Highlight policy boundaries with a thick line.

## C4 — State-transition coverage

**Question:** Which status transitions were tested and observed?

- Chart: directed state graph with edge labels.
- States: investigating, monitoring, resolved.
- Edges: allowed, blocked, untested.
- Add health/recovery preconditions to resolved edge.

## C5 — Hook latency distribution

**Question:** What overhead does deterministic enforcement add?

- Chart: box/violin plot by policy version and tool.
- Separate local predicate time from trusted-state retrieval and transactional
  write time.
- Report median, p95, p99, count, and error rate.
- Do not compare hook microseconds with full model seconds on one unlabeled
  axis.

## C6 — Coverage drift timeline

**Question:** Is a dispatch path bypassing the hook?

- Chart: time series.
- Lines: protected proposals, hook invocations, protected executions.
- Derived panel: invocation coverage = invocations/proposals.
- Alert annotation: executions stable while invocations drop.

## C7 — Policy-version rollout

**Question:** Did a new antidote change only intended decisions?

- Chart: grouped decision counts for old, canary, and promoted versions.
- Facets: scenario/failure category.
- Include historical scenario replay and live canary separately.
- Annotate intended and unexpected decision deltas.

## Data provenance footer

Every measured chart must include:

- repository revision;
- policy and hook code version;
- protected tool inventory;
- trusted-state source/version;
- scenario set and run count;
- deterministic versus live-model data label;
- missing/error handling;
- concurrency/atomicity configuration; and
- measurement window.
