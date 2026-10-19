# Illustrative Skill-Loading Results

> **ILLUSTRATIVE DATA — NOT A BENCHMARK**

These numbers are designed to teach interpretation. They were not produced by
the repository demo and must not be presented as measured course results.

## Routing outcomes across 12 tasks

| Outcome | Count |
| --- | ---: |
| Relevant selections | 17 |
| Irrelevant selections | 3 |
| Relevant omissions | 2 |
| Tasks with no relevant skill | 2 |
| Correct no-skill decisions | 1 |

For tasks with at least one labeled relevant skill:

```text
precision = 17 / (17 + 3) = 85.0%
recall    = 17 / (17 + 2) = 89.5%
```

The omission count matters even though both percentages look strong. Review
which procedures were missed and whether those tasks failed downstream.

## Paired serving comparison

| Metric | Eager baseline | On-demand skills | Interpretation |
| --- | ---: | ---: | --- |
| Complete skill characters supplied | 14,200 | 5,100 | Selective loading reduced detailed skill payload. |
| Model cycles | 1 | 2 | Selection added a call. |
| Mean input tokens | 4,600 | 3,700 | Total input decreased in this illustration. |
| Mean serving latency | 2.8 s | 4.1 s | Extra cycle increased latency. |
| Accepted final outputs | 8/12 | 10/12 | Quality improved on two tasks in this illustration. |
| Selection/fallback errors | N/A | 1/12 | New architecture introduced a new failure mode. |

## Correct teaching conclusion

The illustrative result shows a tradeoff, not a universal winner. On-demand
loading used less detailed context and improved accepted outputs in this small
example, while adding latency and a routing failure mode. A production decision
would require repeated runs, representative tasks, error severity analysis,
and cost measurements from the actual deployment.
