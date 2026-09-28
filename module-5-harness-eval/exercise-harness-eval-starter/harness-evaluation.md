# Harness Evaluation

Complete this document after implementing the evaluation TODOs and running the
full ablation study. Replace every TODO with evidence from `reports/results.csv`,
`reports/failures.json`, and `reports/evaluation_report.md`. Do not invent or
estimate missing results; identify missing coverage as a limitation instead.

## Study scope

TODO: Record the model, randomization seed, number of repetitions, core tasks,
six configurations, run date, and whether the declared study plan completed.

| Item | Value |
| --- | --- |
| Model | TODO |
| Seed | TODO |
| Runs per task/configuration | TODO |
| Planned trials | TODO |
| Recorded trials | TODO |
| Completion status | TODO |

## Configuration results

TODO: Summarize the measured values. Use `N/A` where coverage is incomplete.

| Configuration | Success | Blind quality | Invalid actions | Unauthorized actions | Mean serving tokens | Mean serving seconds | Qualifies? |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | :---: |
| `full` | TODO | TODO | TODO | TODO | TODO | TODO | TODO |
| `no-skills` | TODO | TODO | TODO | TODO | TODO | TODO | TODO |
| `no-evaluator` | TODO | TODO | TODO | TODO | TODO | TODO | TODO |
| `no-hooks` | TODO | TODO | TODO | TODO | TODO | TODO | TODO |
| `no-permissions` | TODO | TODO | TODO | TODO | TODO | TODO | TODO |
| `bare` | TODO | TODO | TODO | TODO | TODO | TODO | TODO |

## Component recommendations

Compare each one-component ablation with `full`. Cite both overall results and
the target tasks for that component. Include failure-category changes and cost
changes only when the compared rows and metric coverage are complete.

| Component | KEEP / REMOVE / OPTIONAL | Measured benefit | Measured cost | Evidence |
| --- | --- | --- | --- | --- |
| Skills | TODO | TODO | TODO | TODO |
| Online evaluator | TODO | TODO | TODO | TODO |
| Hooks | TODO | TODO | TODO | TODO |
| Permissions | TODO | TODO | TODO | TODO |

## Minimum viable harness

TODO: State which configuration is the smallest one that meets every required
threshold. Explain why it qualifies, or explain why no configuration qualifies.
Do not make a global recommendation unless the report marks the study as ready.

## Is the bare agent sufficient?

TODO: Answer with measured task, safety, quality, and cost evidence. Remember
that `bare` removes four components at once, so it is a baseline rather than a
single-variable estimate of any component.

## Limitations and next experiment

TODO: Discuss trial count, model variability, judge limitations, task coverage,
missing measurements, and at least one next experiment that would strengthen
the recommendation.
