# Deterministic Hooks and Antidotes in Harness Loops

Instructional collateral for **Module 3: Hooks and Deterministic Antidotes**.

This package is for instructor review, video recording, slide production, and
exercise alignment. It uses the `INC-2048` mutation demo as its running example
and connects that example to the expense-report hook exercise.

## Teaching thesis

A model call is probabilistic; a correctly implemented hook can still make a
specific harness decision deterministic. For the same validated input, trusted
state, policy version, and code version, the hook returns the same allow/block
result. Placing that decision immediately before a side effect prevents a
known invalid proposal from reaching the tool.

The course calls each exact check an **antidote** because it targets a known
failure mode. A hook is the lifecycle mechanism that runs the antidotes. The
tool performs the action. These are separate responsibilities:

```text
known failure -> explicit invariant -> deterministic antidote
                                          |
model proposal -> before-tool hook --------+-> allow or block -> tool
```

Deterministic does not mean infallible. A hook can be incomplete, use stale or
untrusted inputs, run at the wrong event, be bypassed, contain a bug, or protect
only one execution path. Reliability comes from precise rules, trusted state,
correct placement, fail-closed behavior, atomic execution where needed, tests,
and observable evidence.

## Package map

```text
hook_engineering/
├── README.md
├── module_overview.md
├── learning_objectives.md
├── scripts/       complete narration for five short lessons
├── slides/        slide-by-slide production storyboards
├── visuals/       diagram, chart, and asset specifications
├── examples/      antidote design, hook code, tests, and worked evidence
├── references/    annotated primary and official sources
└── instructor_review.md
```

## Recommended review order

1. Read `module_overview.md` and `learning_objectives.md`.
2. Approve the definitions of deterministic hook and antidote.
3. Review `examples/antidote_design_workbook.md`.
4. Review the hook pseudocode and test matrix.
5. Review each script beside its matching storyboard.
6. Resolve `instructor_review.md` before recording.

## Editorial conventions

- **Tool call** means a model proposal until the harness returns execution
  evidence.
- **Hook** means application code registered at a defined lifecycle event.
- **Before-tool hook** means a hook that runs after call parsing and before tool
  dispatch.
- **Invariant** means a property that must hold at a specified boundary.
- **Antidote** means a deterministic check designed to detect or prevent one
  known failure pattern. This is course terminology, not an API primitive.
- **Trusted state** means application-resolved data used for the decision,
  rather than an unsupported model claim.
- **Fail closed** means uncertainty, malformed input, or check failure prevents
  the protected action.

Live model behavior must be described as observed. Scripted states and sample
metrics are labeled illustrative and must not be presented as benchmark data.

## Repository alignment

The narration references:

- `demo/hooks.py`
- `demo/agent.py`
- `demo/tools.py`
- `demo/models.py`
- `demo/scenarios/*.json`
- `exercise-hooks-starter/hooks.py`
- `exercise-hooks-starter/test_hooks.py`
- `solution/hooks.py`

The demo implements a before-mutation hook over an in-memory incident. The
exercise implements a before-submission hook over an expense report. Production
systems with shared state also need transactional or conditional execution to
avoid a time-of-check/time-of-use gap.
