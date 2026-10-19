# Learning Objectives

## Module-level objectives

By the end of this module, learners will be able to:

1. **Define hook determinism precisely.** Explain that fixed validated inputs,
   trusted state, policy, and code yield the same hook decision without claiming
   the whole agent loop is deterministic.
2. **Distinguish proposal from execution.** Treat a model tool call as a
   proposal until the harness returns evidence that the tool ran.
3. **Locate the correct lifecycle boundary.** Place a safety hook after parsing
   and trusted-state resolution but before a protected side effect.
4. **Design deterministic antidotes.** Convert a known failure pattern into an
   explicit invariant, input contract, predicate, and actionable violation.
5. **Choose deterministic criteria.** Use hooks for objective, computable rules
   and route ambiguous judgments to models or humans without delegating exact
   execution invariants.
6. **Implement fail-closed validation.** Block unknown tools, malformed
   arguments, missing evidence, invalid values, and check errors.
7. **Combine complete findings.** Run every applicable check, distinguish
   pass/fail/error/not-applicable, and allow only when all required checks pass.
8. **Preserve reliable state across cycles.** Canonicalize mutation signatures,
   prevent replay, invalidate stale evidence after mutation, and bound retries.
9. **Address concurrent state.** Explain why real check-and-write operations may
   need transactions, locks, version checks, or atomic conditional APIs.
10. **Return controlled feedback.** Send block evidence through the tool-result
    channel so the model can explain or recover without executing the action.
11. **Test hook coverage.** Verify exact thresholds, malformed values, allow and
    block paths, integration order, bypass resistance, and actual non-execution.
12. **Operate deterministic controls.** Log decision inputs and versions,
    monitor allow/block/error rates, stage policy changes, and document residual
    risk.

## Lesson-level objectives

### Video 1 — Determinism at the execution boundary

Learners can:

- contrast probabilistic generation with deterministic predicates;
- state the fixed-input conditions required for reproducibility;
- explain which execution failures a hook can eliminate; and
- identify claims that overstate determinism.

### Video 2 — Place hooks in the lifecycle

Learners can:

- diagram the function-call, hook, and tool-result sequence;
- explain why validation after execution is too late;
- distinguish before-tool, after-tool, before-completion, and cycle hooks; and
- place permission, safety, execution, and evaluation in the correct order.

### Video 3 — Turn failures into antidotes

Learners can:

- derive an invariant from a concrete observed failure;
- choose trusted inputs and exact comparison semantics;
- write pure, composable checks with useful findings;
- distinguish an antidote from a broad aspiration; and
- preserve not-applicable and error states where needed.

### Video 4 — Engineer a reliable hooked loop

Learners can:

- parse and validate proposed calls before policy evaluation;
- run all relevant antidotes and combine the result;
- block without dispatch and return violations to the model;
- manage replay, stale evidence, retries, and state transitions; and
- explain when atomic check-and-write is required.

### Video 5 — Test and operate deterministic controls

Learners can:

- create truth tables and exact threshold tests;
- verify hook wiring with a fake model and instrumented tool;
- test bypasses and fail-closed error behavior;
- separate deterministic-policy evidence from live-model behavior; and
- monitor, version, canary, and roll back hook policies.

## Suggested knowledge checks

1. A hook calls an LLM to decide whether an expense “looks reasonable.” Is the
   decision deterministic? What would make part of the policy deterministic?
2. A report is validated when first loaded, then submitted ten minutes later.
   What state or TOCTOU risks remain?
3. The model never requests `submit_expense_report`. Did the before-submission
   hook pass?
4. A hook blocks a call, but the tool still executes in a `finally` block. What
   property has the integration violated?
5. An expense of exactly $500 requires approval only when the rule says “$500
   or more.” How do boundary tests expose an incorrect `>` versus `>=`?
6. Why should a successful mutation invalidate previously fresh health
   evidence?
7. Can a safe-remediation skill replace the rollback hook? Why not?

## Performance assessment

A learner demonstrates mastery by producing a harness that:

- identifies every protected side-effect path;
- resolves policy input from authoritative state;
- validates the canonical tool and argument shape;
- runs named deterministic checks without model calls;
- returns a structured allow/block decision and all relevant findings;
- never invokes the protected tool on block or check error;
- sends correlated failure evidence back to the model;
- records proposal, hook, checks, decision, and execution separately;
- passes boundary, malformed-input, replay, and bypass tests; and
- states what remains probabilistic or outside the hook's scope.
