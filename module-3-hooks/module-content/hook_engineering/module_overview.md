# Module Overview

## Module identity

- **Course capability:** Module 3 — Deterministic Hooks in Agent Harnesses
- **Exercise:** Implement expense-policy antidotes before submission
- **Audience:** software developers and AI engineers building agentic systems
- **Target duration:** approximately 32 minutes across five videos
- **Running example:** safe mutation handling for incident `INC-2048`

## Why this module exists

Instructions and skills can improve a model's proposals, but they cannot
guarantee that every proposed action satisfies policy. A post-response
evaluator may detect a mistake after it happens. Neither approach is sufficient
when an invalid side effect must not execute.

Hooks give the harness a deterministic control point. Immediately before a
sensitive tool, ordinary code validates arguments and trusted state against
explicit invariants. Valid proposals reach the tool. Invalid or malformed
proposals return structured violations without performing the side effect.

This makes the loop more reliable in a precise way: it can eliminate execution
of the known invalid actions covered by the checks. It does not make the model,
the whole loop, external services, or unspecified business judgments
deterministic.

## Lesson sequence

| Video | Title | Duration | Central question |
| --- | --- | ---: | --- |
| 1 | Determinism at the execution boundary | 6:00 | What can a deterministic hook guarantee? |
| 2 | Place hooks in the lifecycle | 6:15 | Where must a hook run to control a side effect? |
| 3 | Turn failures into antidotes | 6:30 | How does a known failure become an exact invariant? |
| 4 | Engineer a reliable hooked loop | 7:00 | How do checks, state, feedback, retries, and tools interact? |
| 5 | Test and operate deterministic controls | 6:15 | How do we prove coverage and detect regressions? |

**Total target duration:** 32 minutes.

## Narrative arc

### Act 1: Define determinism narrowly

For fixed validated inputs, trusted state, policy, and code, a pure check
returns the same decision. Contrast that with model judgment and make clear that
the model still decides what to propose and whether to continue.

### Act 2: Put the control at the last safe moment

Intercept parsed tool calls before execution. Resolve trusted state, run every
applicable check, combine results, and execute only on allow. A later evaluator
cannot retroactively prevent a side effect.

### Act 3: Build antidotes from observed failures

Use a repeatable design method:

```text
failure pattern
  -> violated invariant
  -> exact boundary and scope
  -> trusted input contract
  -> deterministic predicate
  -> actionable violation
  -> boundary and adversarial tests
```

### Act 4: Strengthen loop reliability

Handle malformed calls, stale evidence, duplicate actions, retries, state
changes, and controlled feedback. Serialize state-dependent mutations or make
the check-and-write atomic. Keep authorization, validation, tool execution, and
final evaluation as distinct decisions.

### Act 5: Demand coverage evidence

Test every protected path, exact threshold, malformed value, allow path, block
path, and bypass attempt. Log hook version, trusted-input version, named checks,
decision, violation evidence, and whether the tool actually executed.

## What deterministic means here

A hook decision is deterministic under a declared decision context:

```text
decision = f(
    canonical tool name,
    validated arguments,
    trusted state snapshot,
    prior execution evidence,
    policy version,
    hook code version,
)
```

Holding those inputs fixed yields the same result. If time, random values,
network responses, environment variables, mutable global state, or an LLM are
read inside the check, they become inputs and may destroy reproducibility unless
captured and controlled.

## Deterministic does not mean

- the model always requests the correct tool;
- the model always reaches the protected boundary;
- external state cannot change after validation;
- the rule captures every real-world risk;
- the hook code has no bugs;
- an allowed action will achieve its intended outcome;
- authorization has been checked; or
- the final explanation is correct.

## Antidote catalog from the course

| Known failure | Invariant | Antidote |
| --- | --- | --- |
| Mutation without current health evidence | Fresh health evidence exists for the current state | `check_fresh_health_evidence` |
| Rollback to an unknown version | Target occurs in trusted deployment history | `check_rollback_target_exists` |
| Rollback to an unsafe known version | Target is explicitly last-known-good | `check_rollback_target_last_known_good` |
| Repeated state-changing request | Equivalent mutation has not executed in the run | `check_mutation_not_repeated` |
| Premature incident resolution | Health is `HEALTHY` and recovery is confirmed | `check_resolution_state_valid` |
| Excessive meal expense | Meal amount is at most $100.00 | `check_meal_limit` |
| Unapproved high expense | Amount over $500.00 has approval | `check_manager_approval` |
| Duplicate receipt | Receipt IDs are present and unique | `check_unique_receipts` |
| Incorrect total | Reported total equals item sum to the cent | `check_reported_total` |
| Invalid/nonpositive money | Every amount is finite, cent-precise, and above zero | `check_positive_amounts` |

## Hook lifecycle locations

| Lifecycle point | Suitable deterministic use | Caution |
| --- | --- | --- |
| Before model call | Validate/normalize allowed context and budgets | Does not protect later side effects by itself. |
| Before tool call | Authorize, validate invariants, rate-limit, deduplicate | Must cover every route to the tool. |
| After tool result | Validate/normalize output and invalidate stale evidence | Cannot undo a completed side effect unless the operation is transactional. |
| Before completion | Require evidence, tests, or terminal state | A completion gate is not a mutation gate. |
| On retry/cycle | Enforce budgets and repeated-call limits | State-dependent signatures need canonicalization. |

Module 3 implements `before_tool_call`. Later modules demonstrate additional
lifecycle points and permission ordering.

## Reliable execution path

```text
model function_call
        |
parse and validate schema
        |
resolve identity + trusted state
        |
permission decision (Module 4)
        |
deterministic hook antidotes
        | pass all
atomic/conditional tool execution
        |
postcondition + state/evidence update
        |
structured function_call_output to model
```

On failure, return a structured block result and do not execute the protected
tool.

## Required production concerns

The complete lesson covers:

- explicit hook events and protected tool inventory;
- pure predicates and canonical inputs;
- trusted-state resolution and freshness;
- exact numeric and string semantics;
- applicability, pass, fail, error, and not-applicable states;
- running all applicable checks and aggregating violations;
- malformed input and unknown-target fail-closed behavior;
- authorization-before-validity ordering;
- duplicate and replay protection using canonical signatures/idempotency keys;
- evidence invalidation after mutation;
- serialization, transactions, conditional writes, and TOCTOU risk;
- structured feedback to the model without accidental execution;
- cycle and retry limits;
- deterministic unit, boundary, property, integration, and bypass tests;
- live-model tests as separate orchestration evidence;
- traces, metrics, policy versions, rollout, and rollback; and
- residual-risk documentation for failures no antidote covers.

## Deliberate non-goals

- Making subjective judgments such as whether a meal is “reasonable.”
- Encoding user authorization as incident-state validation.
- Hiding policy inside permissive business tools for the comparison.
- Claiming that one before-tool hook makes an entire agent deterministic.
- Allowing a model to decide whether a mandatory hook runs.
- Treating a block as a process crash.
- Relying on a precheck separated from a real write by uncontrolled shared-state
  changes.

## Completion evidence

Learners should leave with:

1. an antidote design table tied to known failures;
2. pure checks with explicit input contracts;
3. one combined `HookResult` with named findings;
4. a before-tool integration that cannot dispatch on block;
5. allow, block, malformed, boundary, and bypass tests;
6. exact money handling with `Decimal` in the expense exercise;
7. a trace that distinguishes requested from executed actions; and
8. an explanation of residual risk and the next required control.
