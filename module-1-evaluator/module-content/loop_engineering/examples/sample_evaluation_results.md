# Illustrative Evaluation Results

> **ILLUSTRATIVE DATA — NOT AN EMPIRICAL BENCHMARK**

These synthetic values demonstrate metric calculation and chart design. They
were not produced by the Module 1 demo and must not be presented as evidence
about any model or provider.

## Evaluation design represented by the sample

- 20 instructor-labeled cases
- 12 reference-acceptable candidates
- 8 reference-unacceptable candidates
- same hypothetical generator and task cases in both paths
- self-evaluation versus independent evaluation

## Decision counts

### Self-evaluation

| Harness decision | Reference acceptable | Reference unacceptable | Total |
| --- | ---: | ---: | ---: |
| Accept | 11 | 5 | 16 |
| Reject | 1 | 3 | 4 |
| Total | 12 | 8 | 20 |

### Independent evaluation

| Harness decision | Reference acceptable | Reference unacceptable | Total |
| --- | ---: | ---: | ---: |
| Accept | 10 | 1 | 11 |
| Reject | 2 | 7 | 9 |
| Total | 12 | 8 | 20 |

## Calculated metrics

| Metric | Self-evaluation | Independent evaluation |
| --- | ---: | ---: |
| Acceptance rate | 16/20 = 80.0% | 11/20 = 55.0% |
| False acceptance rate | 5/8 = 62.5% | 1/8 = 12.5% |
| False rejection rate | 1/12 = 8.3% | 2/12 = 16.7% |
| Initial rubric mean | 3.1/5 | 3.1/5 |
| Final rubric mean | 3.7/5 | 4.2/5 |
| Mean attempts | 1.4 | 1.8 |
| Mean generator/revision tokens | 1,500 | 1,650 |
| Mean evaluator tokens | 500 | 1,100 |
| Mean total tokens | 2,000 | 2,750 |
| Mean total latency | 3.2 s | 5.8 s |

## Interpretation

In the illustration, independent evaluation substantially reduces false
acceptance but increases false rejection, attempts, token use, and latency. The
correct architecture choice depends on task risk and product constraints.

For a high-impact incident update, avoiding four additional false acceptances
may justify the overhead. For a low-risk draft always reviewed by a human, the
same tradeoff may not.

Acceptance rate alone would make self-evaluation look better because it accepts
more output. The reference comparison reveals that five of those acceptances
are wrong. This is why evaluation decisions must be scored against external
labels.

## Quality improvement per token

Using the illustrative means:

```text
self quality gain = 3.7 - 3.1 = 0.6
independent quality gain = 4.2 - 3.1 = 1.1

additional independent tokens = 2,750 - 2,000 = 750
additional quality gain = 1.1 - 0.6 = 0.5

incremental gain per 1,000 additional tokens = 0.5 / 0.75 = 0.67 rubric points
```

This ratio is only meaningful when rubric scores are calibrated and comparable.
It should be reported beside error rates, not used as a single universal KPI.

## Requirements for a real study

Replace the sample values with:

- held-out case IDs and reference labels;
- model and provider versions;
- generator and evaluator prompt versions;
- sampling parameters;
- repetition count and randomization method;
- raw candidate and finding records;
- token, cost, and latency coverage;
- confidence intervals or observed dispersion; and
- documented human adjudication of disagreements.
