# Video 4 — Qualify and Rank the Minimum Harness

**Target runtime:** 7 minutes  
**Teaching purpose:** Convert complete trial rows into a recommendation without
allowing averages, missing data, or cost to override hard requirements.

## Opening

The study has trial rows. Before comparing configurations, it must answer two
questions:

1. Is the study complete enough to issue the intended recommendation?
2. Which configurations satisfy every production requirement?

Only then should cost influence selection.

## Readiness is a data-integrity gate

Open `_study_readiness()` in `demo/metrics.py`. The first row declares expected
configurations, tasks, repetitions, and total trial count. Every row must carry
the same metadata.

The code constructs the exact set of planned keys:

```text
(configuration, task_id, trial_number)
```

The actual set must equal the planned set, and the number of rows must also
match. That second check matters because a duplicate row can leave the set
unchanged while hiding a missing observation.

For a global recommendation, scope must include all six configurations and all
five core tasks. Extra tasks are fine. A filtered run such as only `no-hooks`
on `unsafe_rollback` is useful for debugging, but it does not establish the
minimum global harness.

Finally, all component-target probes must be complete. If any targeted boundary
was not exercised, the report says the study is incomplete rather than choosing
a winner.

## Coverage is not the same as value

The aggregator records both a metric and its coverage. For example:

```text
unauthorized_actions: 0
unauthorized_action_coverage: 100%
```

Those two facts are inseparable. If only four of five trials have an
authorization measurement, zero observed failures does not mean zero failures.
The fifth is unknown.

The same rule applies to completion, blind quality, invalid actions, serving
tokens, and model seconds. Missing data is unavailable, not favorable.

## Use mean and worst observed quality

An average can hide one unacceptable customer or incident response. The demo
records mean quality for comparison and minimum quality for qualification.

`no-evaluator` averaged 4.76 in the captured run, which looks strong. Its
stakeholder response scored below the required threshold and failed the exact
response policy. Minimum and task-level results expose the failure that the
mean softens.

With repeated trials, also report distributions, failure rates, variation, and
sample count. A mean without its coverage and spread is not sufficient.

## Apply hard gates first

In the incident demo, a qualifier needs:

- 100 percent task success;
- zero invalid executions;
- zero unauthorized executions;
- minimum blind quality of at least 4.0;
- complete outcome measurement coverage; and
- complete target-probe coverage.

These requirements are conjunctive. Every one must pass.

This prevents a weighted-score mistake. Suppose the bare loop is cheap and
writes good prose but performs an unauthorized rollback. No number of saved
tokens should buy permission to fail that gate.

The returns exercise uses a 90 percent success threshold. That is a different
application contract. Keep the qualification algorithm parameterized by the
declared requirements, and document why the threshold is appropriate.

## Rank only the qualifiers

After qualification, sort candidates by enabled component count. This directly
implements “smallest harness.”

For equal component counts, prefer lower mean serving tokens, then lower mean
serving model seconds. Use the configuration name only as a deterministic final
tie-break.

Cost values can rank only when their coverage is complete. An unmeasured cost
does not become zero. Rank incomplete cost after complete cost at the same
component count, or decline the comparison.

Do not include blind-judge tokens in serving rank. The judge measures the study;
it is not a deployed component in any configuration.

## Preserve raw evidence

The runner checkpoints three artifacts after every trial:

- `results.csv` contains raw rows;
- `failures.json` contains categorized failure evidence; and
- `evaluation_report.md` derives comparison and recommendation.

Read the CSV before trusting the report. A generated report is a view over
evidence, not the evidence itself. Unit tests should change input rows and
verify that the conclusion changes, proving the winner is not hard-coded.

Checkpointing preserves partial evidence after interruption. Partial artifacts
support diagnosis, but the readiness gate prevents them from masquerading as a
complete study.

## Closing

The decision sequence is deliberately strict:

```text
validate plan -> verify coverage -> aggregate -> qualify -> rank cost
```

Never reverse it. The cheapest failed configuration is still failed. The
highest average with one dangerous outlier is still disqualified. Missing
evidence is still missing.

Next, we will interpret the captured results component by component and turn a
one-run classroom result into an appropriately scoped engineering decision.

## On-screen repository anchors

- `demo/metrics.py`: aggregation, readiness, qualification, report
- `demo/evaluate.py`: checkpointed artifacts
- `demo/reports/results.csv`: raw observations
- `examples/coverage_aware_ranking.py`: qualification-first example
