# Video 3 — Turn Failures into Deterministic Antidotes

**Target duration:** 6 minutes 30 seconds  
**Learning objective:** Convert observed failures into exact, composable,
testable checks using trusted inputs and explicit edge semantics.

## Instructor narration

### [Slide 1] What “antidote” means — 0:00–0:50

In this course, an antidote is a deterministic check designed to prevent a
known failure. It is not a provider feature and it is not a claim that every
risk has one simple cure.

Start with a concrete failure: a $185 meal was submitted under a $100 policy,
or a degraded incident was marked resolved. Then state the exact invariant that
would have prevented that event.

The specificity is the value. “Be safer” is advice. “Meal amount must be less
than or equal to $100.00” is executable.

### [Slide 2] Failure to invariant — 0:50–1:45

Use a six-step transformation.

Name the failure. State the invariant. Identify the boundary where it must hold.
List trusted inputs. Write a pure predicate. Return actionable evidence.

For premature resolution, the failure is a transition to `RESOLVED` while the
service remains degraded. The invariant is: immediately before the status
mutation, service health equals `HEALTHY` and recovery confirmation is exactly
true.

Both conditions matter. Replacing them with a model summary such as “service
looks recovered” gives up the deterministic boundary.

### [Slide 3] Trusted inputs and canonical semantics — 1:45–2:45

The proposed action comes from the model; approval evidence must not.

The harness matches the incident ID against the active trusted incident, reads
health and deployment history from application state, and tracks executed
mutations itself. For expense submission, the harness validates the original
loaded report rather than allowing the model to rewrite amounts inside the
submission arguments.

Define canonical semantics before comparing. Normalize only what policy allows.
Sort JSON keys when building an equivalent-mutation signature. Use exact enums
for states. For money, parse a finite decimal value, reject Booleans, NaN,
infinity, and fractions of a cent, and compare `Decimal` values.

Ambiguous normalization creates inconsistent policy.

### [Slide 4] Exact boundaries reveal bugs — 2:45–3:40

The expense exercise has two deliberate thresholds.

A meal of exactly $100.00 passes; $100.01 fails. An individual expense of
exactly $500.00 does not require approval; $500.01 does. Those statements map
to `>` comparisons, not `>=`.

A reported total must equal the line-item sum to the cent. One cent is not
“close enough.” Decimal arithmetic represents these policy values without the
surprises of binary floating-point approximations.

Boundary tests should sit beside every comparison. A consistently wrong
threshold is deterministic but not correct.

### [Slide 5] Compose small checks — 3:40–4:35

Keep antidotes small enough to test independently. The incident hook checks
fresh evidence, target existence, last-known-good status, repetition, and
resolution state separately.

Then run every applicable check and aggregate findings. This gives the operator
all relevant violations in one decision rather than fixing one issue per
retry.

Allow only when every required applicable check passes. A malformed input or
check exception produces an error and fails closed.

For richer production traces, distinguish `PASS`, `FAIL`, `ERROR`, and
`NOT_APPLICABLE`. The small demo uses Boolean checks, so a check that does not
apply appears true because it returned no violation. Do not misread that as an
executed proof.

### [Slide 6] Match antidotes to computable rules — 4:35–5:25

Not every policy is deterministic.

“The receipt ID is unique” is computable. “The meal is reasonable for the
city” is underspecified unless policy supplies a rate table and exact rules.
“The business justification is convincing” requires judgment.

Use deterministic code where the facts and boundary are explicit. Use a model
or human where semantic judgment is genuinely required, but do not let that
inferential decision silently replace exact invariants.

If policy cannot be stated clearly, the first task is policy clarification—not
inventing a Boolean check.

### [Slide 7] Residual risk is part of the design — 5:25–6:10

Every antidote ends with a residual-risk statement.

The last-known-good check does not prove current compatibility. The duplicate
signature check covers only the scope and persistence of its execution record.
The meal threshold does not detect a fabricated receipt. The total check does
not authorize the employee.

Document what the check proves, what it assumes, and which other control owns
the remaining risk. This prevents a growing list of checks from being mistaken
for complete safety.

### [Slide 8] Transition — 6:10–6:30

We now have exact antidotes. Next we will integrate them into a loop that
handles state changes, retries, feedback, and execution without opening a gap
between the decision and the side effect.

## Demonstration cue

Use `examples/antidote_design_workbook.md` to derive the rollback check, then
show the matching function in `demo/hooks.py` and exact thresholds in
`solution/hooks.py`.

## Transition line

> A predicate prevents nothing until the dispatcher honors it and the checked
> state is still valid when the tool runs.
