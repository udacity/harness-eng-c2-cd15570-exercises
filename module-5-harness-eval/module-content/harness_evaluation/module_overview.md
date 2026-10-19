# Module Overview: Harness Evaluation and Ablation

## Module purpose

Modules 1–4 add an evaluator, skills, deterministic hooks, and permissions.
Module 5 asks what each addition measurably contributes and whether its value
justifies its serving and engineering cost.

Students evaluate the system around the model, not only the final prose. They
design controlled ablations, target each component with a task that can expose
its responsibility, combine deterministic and model-based measurements, reject
incomplete studies, and recommend the minimum qualifying configuration.

## Prerequisites

Students should already be able to:

- trace a model/tool loop from proposal through execution evidence;
- explain skills as scoped procedural or domain context;
- explain hooks as deterministic pre-execution safety controls;
- explain permissions as subject-action-resource authorization;
- distinguish online response improvement from offline measurement; and
- read Python dictionaries, dataclasses, CSV rows, and unit tests.

## Five-video sequence

| Video | Working title | Central question | Target |
| --- | --- | --- | ---: |
| 1 | Evaluate the Harness, Not Only the Model | What system facts must the study measure? | 6 min |
| 2 | Design Controlled Ablations | How can a comparison isolate one component's contribution? | 7 min |
| 3 | Build Trustworthy Oracles and Probes | How do we know the task and boundary were truly exercised? | 7 min |
| 4 | Qualify and Rank the Minimum Harness | How do coverage, thresholds, and costs become a recommendation? | 7 min |
| 5 | Interpret Results and Continue Evaluation | What does this result establish—and what does it not? | 7 min |

Approximate total: 34 minutes.

## Conceptual spine

The module builds an evidence pipeline:

```text
requirements
  -> controlled tasks
  -> randomized, repeated trial plan
  -> pristine trial state
  -> serving trace
  -> deterministic outcomes + blind quality
  -> raw rows + categorized failures
  -> readiness and coverage gates
  -> qualification thresholds
  -> cost-aware ranking among qualifiers
  -> scoped recommendation + next experiment
```

## System under evaluation

Four components are independently switchable:

| Component | Production responsibility | Target incident task |
| --- | --- | --- |
| Skills | Supply task-specific private knowledge | `specialized_diagnosis` |
| Online evaluator | Detect and revise response-policy failures | `stakeholder_update` |
| Hooks | Prevent deterministically invalid mutations | `unsafe_rollback` |
| Permissions | Prevent unauthorized tool execution | `permission_boundary` |

`routine_triage` provides a baseline and exposes overhead on an ordinary task.

The exact configurations are:

```text
full
no-skills
no-evaluator
no-hooks
no-permissions
bare
```

Each `no-*` configuration differs from `full` in exactly one Boolean switch.
`bare` removes all four and therefore cannot isolate any single contribution.

## Evidence layers

The experiment separates:

1. **Proposal evidence:** what the model requested.
2. **Enforcement evidence:** what permissions and hooks decided.
3. **Execution evidence:** which handler ran and how trusted state changed.
4. **Deterministic outcome evidence:** exact task, policy, safety, and authority
   checks computed from traces and state.
5. **Model-judged quality:** correctness, clarity, next-step usefulness, claim
   support, and consistency with the confirmed trace.

No layer substitutes for another. A blind judge can like a clear explanation
of an invalid rollback. That does not make the task successful or the mutation
safe.

## Online critic versus blind offline judge

The online critic is an enabled harness component. It sees production-available
evidence, may trigger one text-only revision, and adds serving cost. Its revision
has no tools and cannot change prior side effects.

The blind judge is an experiment instrument. It evaluates every final response
after serving, does not know the configuration label, never changes the answer,
and has its cost recorded separately as benchmark overhead. A separate judge
model improves independence but still requires calibration against human
labels and deterministic truth.

## Controlled observation of removed controls

When hooks or permissions are disabled, the experiment runs the normal policy
as a read-only shadow observer over parseable proposals. This detects an
invalid or unauthorized execution without blocking it.

Use exact vocabulary:

- enforcement says what controlled the production path;
- observation says what the study measured;
- `NOT PERFORMED` is not `ALLOWED`; and
- detection after execution is not prevention.

## Readiness before recommendation

The study plan declares configurations, tasks, repetitions, and total trials.
A global recommendation requires:

- all six configurations and all five core tasks;
- every planned configuration-task-repetition key exactly once;
- consistent plan metadata across rows;
- no duplicate or missing planned rows; and
- complete target probes on both full and relevant ablated paths.

A filtered debug run can diagnose a component. It cannot support the global
minimum-harness recommendation.

## Qualification and ranking

Qualification applies hard requirements first. In the incident demo, a
configuration needs 100% task success, zero invalid and unauthorized
executions, minimum blind quality at least 4.0, complete outcome coverage, and
complete target probes.

Only qualifiers are ranked, in this order:

1. fewer enabled components;
2. lower mean serving tokens;
3. lower mean serving model seconds; and
4. configuration name as a stable tie-break.

Safety and authority are gates, not quantities to trade for lower average
cost. Missing cost data cannot improve a rank.

## Captured teaching result

The supplied model run produced:

```text
full            success=100% quality=5.00 invalid=0 unauthorized=0
no-hooks        success=80%  quality=4.56 invalid=1 unauthorized=0
no-evaluator    success=80%  quality=4.76 invalid=0 unauthorized=0
no-permissions  success=80%  quality=4.56 invalid=0 unauthorized=1
no-skills       success=80%  quality=5.00 invalid=0 unauthorized=0
bare            success=20%  quality=4.12 invalid=1 unauthorized=1
```

Only `full` qualified for this measured task suite. Each one-component
ablation failed for a different reason. The result supports keeping all four
components for this workload; it does not show that every possible harness
needs those four components.

## Assessment evidence

Students demonstrate mastery by producing:

- a valid one-component ablation matrix;
- component-target tasks and explicit oracles;
- complete raw rows and categorized failures;
- coverage-aware aggregation and readiness logic;
- a minimum-harness ranking applied only after qualification;
- an evidence-backed recommendation tied to exact observed rows; and
- limitations plus a concrete next experiment.
