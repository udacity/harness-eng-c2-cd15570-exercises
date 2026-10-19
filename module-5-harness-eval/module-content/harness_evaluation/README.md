# Evaluating Production Harness Loops

Instructional collateral for **Module 5: Harness Evaluation and Ablation**.

This package is for instructor review, video recording, slide production, and
exercise alignment. It evaluates the cumulative `INC-2048` harness built in
Modules 1–4, then transfers the method to the online-store returns exercise.

## Teaching thesis

Every harness component should earn its production cost with measured evidence.
The goal is not the largest loop and not the barest loop. It is the smallest
measured configuration that satisfies the declared task, response-quality,
safety, authorization, coverage, and operational requirements.

```text
production requirement
        |
        v
target task + oracle + threshold
        |
        v
full harness versus one-component ablation
        |
        v
outcomes + failures + serving cost + coverage
        |
        v
qualify configurations, then rank the qualifiers
```

A model proposal, a harness decision, a tool execution, and an evaluator score
are separate facts. The study records all four. Deterministic oracles judge
exact business, safety, and authorization outcomes; a blind model judge scores
open-ended response qualities. Missing measurements never count as passing.

## Package map

```text
harness_evaluation/
├── README.md
├── module_overview.md
├── learning_objectives.md
├── scripts/       complete narration for five short lessons
├── slides/        slide-by-slide production storyboards
├── visuals/       diagrams, charts, and asset specifications
├── examples/      ablation design, oracles, ranking, and results
├── references/    annotated repository and official sources
└── instructor_review.md
```

## Recommended review order

1. Read `module_overview.md` and `learning_objectives.md`.
2. Approve the distinction between model evaluation and harness evaluation.
3. Review `examples/ablation_design_workbook.md` and
   `examples/task_oracle_contract.md`.
4. Review the study-plan and coverage-aware ranking examples.
5. Review each script beside its matching storyboard.
6. Resolve `instructor_review.md` before recording.

## Editorial conventions

- **Trial** means one configuration-task-repetition observation from fresh
  state.
- **Configuration** means one exact set of enabled harness components.
- **Ablation** means a controlled configuration that removes one component
  while holding the remaining study factors fixed.
- **Target task** means a task constructed to exercise a component's distinct
  responsibility.
- **Oracle** means the rule or judge that maps evidence to a measurement.
- **Probe coverage** means the target proposal or component behavior actually
  reached the boundary needed for comparison.
- **Serving cost** means model work on the deployed path, including an enabled
  online critic and revision.
- **Experiment overhead** means measurement work, such as the blind judge,
  that does not change the served result.
- **Qualification** means satisfying every required threshold with complete
  measurement coverage.

Live model behavior must be described as observed. The captured one-repetition
result is a worked example, not statistical proof or a universal architecture
recommendation.

## Repository alignment

The narration references:

- `demo/config.py`
- `demo/tasks.py`
- `demo/agent.py`
- `demo/experiment.py`
- `demo/evaluator.py`
- `demo/metrics.py`
- `demo/evaluate.py`
- `demo/test_demo.py`
- `demo/reports/*`
- `exercise-harness-eval-starter/INSTRUCTIONS.md`
- `solution/config.py`
- `solution/metrics.py`
- `solution/test_harness.py`

The incident demo requires 100% task success; the returns exercise uses its own
declared 90% success threshold. Teach thresholds as application decisions and
always read them from the system under evaluation rather than assuming one
course-wide value.
