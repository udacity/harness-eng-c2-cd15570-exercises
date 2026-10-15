# Loop Engineering in the Harness

Instructional collateral for **C2.1 / I2.1: Generator–Evaluator Separation**.

This package is for instructor review, video recording preparation, and slide
development. It does not contain finished video assets. The material uses the
Module 1 `INC-2048` incident-update demo as its main thread and connects that
demo to the customer-support exercise.

## Teaching thesis

The generator should not be the sole authority deciding whether its own work is
correct. A production harness should separate generation from acceptance,
apply deterministic checks wherever correctness is computable, use calibrated
inferential evaluation where judgment is necessary, and retain evidence for
its stop decision.

Separation does not make an evaluator automatically correct. It creates an
independent responsibility, prompt, context, and acceptance boundary that can
be tested, calibrated, and replaced.

## Package map

```text
loop_engineering/
├── README.md
├── module_overview.md
├── learning_objectives.md
├── scripts/       complete narration for five short lessons
├── slides/        slide-by-slide production storyboards
├── visuals/       diagram, chart, and asset specifications
├── examples/      prompts, rubric, pseudocode, and worked evidence
├── references/    annotated primary sources
└── instructor_review.md
```

## Recommended review order

1. Read `module_overview.md` and `learning_objectives.md` to confirm scope.
2. Review the examples, especially the rubric and loop pseudocode.
3. Review each narration script beside its matching storyboard.
4. Approve the visual language before producing slides.
5. Resolve the questions in `instructor_review.md` before recording.

## Editorial conventions

- **Generator** means the model call responsible for producing or revising a
  candidate.
- **Self-evaluator** means review performed inside the generator's continuing
  conversation.
- **Independent evaluator** means a separate call with its own instructions
  and context. It may use the same model family.
- **Deterministic check** means code or a tool computes the outcome from an
  explicit rule.
- **Inferential check** means a model or human applies judgment to evidence.
- **Accepted** means every declared acceptance condition passed. It does not
  mean the output is universally correct.

Live model behavior must be described as observed. Scripted failures and sample
metrics are labeled as illustrations and must not be presented as benchmark
results.

## Connection to the repository

The narration references these Module 1 demo files:

- `demo/scenarios/inc_2048.json`
- `demo/harness/generator.py`
- `demo/harness/loops/basic_loop.py`
- `demo/harness/loops/self_evaluation_loop.py`
- `demo/harness/loops/external_evaluation_loop.py`
- `demo/main.py`

The initial exercise emphasizes inferential separation so students can see the
behavioral contrast. Deterministic checks are introduced as the next concrete
engineering improvement and are fully represented in the target architecture.
