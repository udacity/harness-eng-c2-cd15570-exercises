# Chart and Table Specifications

Use actual generated rows for result charts. Label repetition count, model,
judge model, and task suite. Never convert the captured example into a general
benchmark.

## Chart 1 — Configuration matrix

**Type:** Boolean heatmap  
**Rows:** full, no-skills, no-evaluator, no-hooks, no-permissions, bare  
**Columns:** skills, evaluator, hooks, permissions

Add a rightmost column showing changed fields relative to `full`. Every
`no-*` row must show exactly one.

## Chart 2 — Component-target comparison

**Type:** Four paired small multiples

Each panel contains:

- full versus matching ablation;
- target-task success;
- component-specific oracle;
- probe coverage;
- serving cost delta; and
- exact failure category.

Do not place bare in these causal panels.

## Chart 3 — Quality distribution by configuration

**Type:** Dot plot or box plot for repeated studies  
**Required overlays:** mean, minimum, threshold, sample count, coverage.

For one repetition per task, use individual task dots instead of a box plot.
Do not imply a distribution from five heterogeneous task values.

## Chart 4 — Safety and authorization events

**Type:** Two-column count table

| Configuration | Invalid executions | Unauthorized executions |
| --- | ---: | ---: |

Pair counts with measurement coverage and total trials. Zero without complete
coverage is displayed as unavailable.

## Chart 5 — Serving versus experiment cost

**Type:** Stacked bars in separate panels

Serving panel may include generator, online critic, revision. Experiment panel
contains blind judge. Never stack both into a single “configuration cost” used
for minimum-harness ranking.

## Chart 6 — Readiness grid

**Type:** Configuration × task × repetition tile matrix

Tile states:

- recorded and complete;
- recorded with trial error;
- missing;
- duplicate; and
- target probe unexercised.

The study-ready badge turns green only when scope, plan, and probes pass.

## Chart 7 — Captured result

**Type:** Exact result table, not decorative bar chart

| Configuration | Success | Mean quality | Invalid | Unauthorized |
| --- | ---: | ---: | ---: | ---: |
| full | 100% | 5.00 | 0 | 0 |
| no-skills | 80% | 5.00 | 0 | 0 |
| no-evaluator | 80% | 4.76 | 0 | 0 |
| no-hooks | 80% | 4.56 | 1 | 0 |
| no-permissions | 80% | 4.56 | 0 | 1 |
| bare | 20% | 4.12 | 1 | 1 |

**Mandatory subtitle:** Captured one-repetition incident study; illustrative of
the method, not a production benchmark.

## Chart 8 — Evaluation maturity roadmap

**Type:** Layered roadmap

1. deterministic unit fixture;
2. live single-run smoke study;
3. repeated randomized study;
4. held-out and adversarial set;
5. human-calibrated judge;
6. change-gated continuous evaluation;
7. monitored production feedback loop.

Do not imply later stages eliminate uncertainty.
