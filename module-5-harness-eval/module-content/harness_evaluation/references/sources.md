# Sources and Research Notes

Accessed October 18, 2026. Recheck changing documentation and repository
behavior before final recording.

## R1 — Incident harness evaluation implementation

Primary local sources:

- `module-5-harness-eval/demo/README.md`
- `module-5-harness-eval/demo/config.py`
- `module-5-harness-eval/demo/tasks.py`
- `module-5-harness-eval/demo/agent.py`
- `module-5-harness-eval/demo/experiment.py`
- `module-5-harness-eval/demo/evaluator.py`
- `module-5-harness-eval/demo/metrics.py`
- `module-5-harness-eval/demo/evaluate.py`
- `module-5-harness-eval/demo/test_demo.py`

**Relevant use:** Authoritative source for the six configurations, five target
tasks, 100% success gate, trace semantics, shadow observation, online/offline
cost split, target-probe coverage, readiness gate, ranking, and artifacts.

**Guardrail:** The captured 30-trial result uses one repetition. It demonstrates
the method and one observed outcome, not stable effect size or universal
production assurance.

## R2 — Returns exercise and solution

Primary local sources:

- `module-5-harness-eval/exercise-harness-eval-starter/INSTRUCTIONS.md`
- `module-5-harness-eval/exercise-harness-eval-starter/test_harness.py`
- `module-5-harness-eval/solution/config.py`
- `module-5-harness-eval/solution/metrics.py`
- `module-5-harness-eval/solution/test_harness.py`
- `module-5-harness-eval/solution/README.md`

**Relevant use:** Transfers controlled ablation, coverage-aware qualification,
study readiness, artifact generation, and written recommendation to the store
domain. The returns exercise declares a 90% success threshold and its own
oracles.

**Guardrail:** Do not copy incident result values into the returns analysis.
Each system must generate and interpret its own rows.

## R3 — Captured result and instructor interpretation

Primary local sources:

- `module-5-harness-eval/demo/reports/results.csv`
- `module-5-harness-eval/demo/reports/failures.json`
- `module-5-harness-eval/demo/reports/evaluation_report.md`
- `module-5-harness-eval/demo/harness-evaluation.md`
- `module-5-harness-eval/demo/script.md`

**Relevant use:** Supplies the observed success, quality, invalid, unauthorized,
and serving-cost values and the component-by-component interpretation.

**Guardrail:** `harness-evaluation.md` also contains a deterministic fixture
example with different quality values. Keep fixture and captured model evidence
clearly labeled and do not merge their numbers.

## R4 — Evaluation best practices

**OpenAI.** “Evaluation best practices.”  
[Official OpenAI documentation](https://developers.openai.com/api/docs/guides/evaluation-best-practices)

**Relevant use:** Supports task-specific evaluation, early and continuous
evaluation, logging, automated scoring where appropriate, human calibration,
production-representative datasets, and coverage of typical, edge, and
adversarial cases.

**Guardrail:** This course implements a local Python evaluation workflow; it
does not require or document a hosted Evals product. Product availability and
API lifecycle details are outside this package and must be checked separately.

## Claim-to-source map

| Course claim | Source | Approved phrasing |
| --- | --- | --- |
| Each `no-*` row changes one component | R1, R2 | “Compare full with the matching one-switch ablation.” |
| Bare cannot isolate one component | R1 | “Bare is a combined baseline, not a causal estimate.” |
| Exact outcomes come from trace and state | R1, R2 | “Use deterministic oracles for business and boundary facts.” |
| Online critic cost belongs to serving | R1 | “It can change the served response and counts against that configuration.” |
| Blind judge cost is experiment overhead | R1 | “It scores after serving and does not rank deployed cost.” |
| Probe coverage is required | R1 | “No prevention claim without the target proposal reaching both paths.” |
| Task-specific, continuous evals need human calibration | R4 | “Grow and calibrate the suite over the system lifecycle.” |
| Full is minimum qualifying in the captured study | R3 | “For this measured workload and run, only full qualified.” |

## Citation and recording policy

1. Identify local implementation behavior as repository-specific.
2. Label deterministic fixtures and live model observations separately.
3. State sample count and task scope beside result claims.
4. Never turn missing coverage into zero failures.
5. Do not claim causation from `full` versus `bare`.
6. Do not claim a model judge establishes exact safety or authorization truth.
7. Do not claim the captured result generalizes to every production harness.
8. Recheck official documentation before recording current product claims.
9. Keep source quotations short; prefer paraphrase and code evidence.
