# Visual Asset Plan

## Required reusable assets

- Four-switch harness configuration panel.
- Configuration card showing name and enabled components.
- Task card with target component and oracle fields.
- Trial ledger row with configuration, task, repetition, and model version.
- Proposal, permission, hook, execution, state, and evaluator event icons.
- Deterministic code-ruler icon.
- Online critic icon with text-only revision arrow.
- Blind judge icon with obscured configuration label.
- Shadow observer booth with dashed connections.
- Coverage card with value and numerator/denominator.
- Hard qualification gate and separate cost-ranking scale.
- Raw CSV, failures JSON, and report document cards.

## Color and shape system

| Meaning | Color | Shape/label |
| --- | --- | --- |
| Proposal | Amber | Dashed event, `PROPOSED` |
| Trusted trace/state | Blue | Solid ledger record |
| Passed deterministic check | Green | Square check, `PASS` |
| Hard requirement failure | Red | Stop shape, reason label |
| Model evaluator/judge | Purple | Hexagon, role label |
| Observer-only decision | Blue-gray | Dashed eye, `OBSERVED` |
| Missing/unavailable | Gray | Hollow cell, `UNAVAILABLE` |

Color must never carry meaning alone.

## Code-capture plan

Capture short excerpts:

1. `demo/config.py`: exact matrix.
2. `demo/tasks.py`: core task set and validation.
3. one target scenario's request and oracle.
4. `demo/agent.py`: enforcement and shadow fields.
5. `demo/evaluator.py`: separate online and blind instructions.
6. `demo/experiment.py`: serving versus benchmark calls.
7. `demo/metrics.py`: deterministic oracle.
8. `demo/metrics.py`: aggregation coverage.
9. `demo/metrics.py`: readiness and probe checks.
10. `demo/metrics.py`: qualification-before-ranking.

Use line highlighting at a readable 1080p size. Redact `.env`, tokens, local
usernames, endpoint credentials, and absolute home paths.

## Result-capture plan

- Show the trial-plan header before results.
- Capture at least one proposal, denial/block, and actual execution event.
- Open raw `results.csv` before the Markdown report.
- Show target-task rows beside the aggregate row.
- Display both mean and minimum quality.
- Label model, judge, runs, seed, and task scope.
- Do not animate a recommendation until readiness is visibly complete.

## Accessibility and editorial checks

- Every color has a text or shape equivalent.
- Tables have clear reading order and sufficient contrast.
- Large values include units and denominators.
- Acronyms such as CSV are either familiar in context or expanded.
- Avoid rapidly changing dense terminal output; freeze and highlight evidence.
- Synthetic fixture results say “fixture”; live results say “observed.”
- Never show a confidence interval when the study did not compute one.
- Never show an absent measurement as zero.

## Third-party assets

No third-party image is required. Prefer original vector diagrams, repository
code captures, and fictional incident/store data. Record any later external
asset in the course's third-party asset ledger before publication.
