# Video 1 — Determinism at the Execution Boundary

**Target duration:** 6 minutes  
**Learning objective:** Define deterministic hook behavior precisely and
explain the reliability guarantee it can—and cannot—provide.

## Instructor narration

### [Slide 1] A probabilistic model can use a deterministic gate — 0:00–0:50

In Module 2, the safe-remediation skill told the model to verify a rollback
target before recommending a production change. That guidance improves the
proposal, but the model can still omit a step or request the wrong target.

Module 3 adds a different kind of component. A before-tool hook runs ordinary
Python at the execution boundary. It does not ask the model whether the action
looks safe. It computes whether declared invariants hold and returns allow or
block.

The model remains probabilistic. The gate can still be deterministic.

### [Slide 2] Define determinism by inputs — 0:50–1:50

For this module, deterministic means: given the same validated tool name,
canonical arguments, trusted state snapshot, prior execution record, policy
version, and hook code, the hook returns the same decision.

Think of the decision as a function. If those inputs are fixed, the output is
fixed. No model call, sampling temperature, or natural-language judgment occurs
inside the check.

If a hook reads the current clock, calls a changing service, consults random
values, or uses mutable global state, those are additional inputs. Capture them
explicitly or the decision will not be reproducible.

Determinism is therefore a property of a declared decision context, not a
magical label attached to any Python function.

### [Slide 3] The concrete incident decision — 1:50–2:45

In `INC-2048`, the operator asks to roll production back to `checkout-v40`.
Trusted deployment history contains that version, but marks `checkout-v41` as
last-known-good.

The rollback antidote computes an exact predicate: does one history entry have
the requested version and `last_known_good is True`?

For this snapshot, the answer for v40 is false. The hook blocks. For v41, the
answer is true, assuming every other required invariant also passes. The
decision does not change because the model argues more confidently.

This is the reliability gain: an invalid proposal covered by the rule cannot
cross this dispatcher when the hook is correctly wired.

### [Slide 4] What becomes more reliable — 2:45–3:45

A deterministic hook can make specific loop properties more reliable.

It can require fresh evidence before mutation, reject malformed arguments,
enforce exact thresholds, prevent forbidden state transitions, deduplicate
replayed actions, and ensure that blocked calls do not reach the tool.

It also produces stable failure categories. Instead of a different explanation
on every run, the harness can return `TARGET_NOT_LAST_KNOWN_GOOD` with the same
meaning each time. The model may phrase the final explanation differently, but
the execution decision and trace remain stable.

This separates an unpredictable proposal path from a predictable control path.

### [Slide 5] What remains nondeterministic or unknown — 3:45–4:45

The hook does not force the model to request a tool. If the model answers early,
the hook never runs. It does not prove that deployment history is true or
fresh. It does not know whether the user is authorized unless a permission
decision is supplied. It does not guarantee the rollback will succeed or
restore service.

And it only covers encoded failures. A last-known-good flag may be insufficient
if compatibility, database migrations, or regional state also matter.

So the correct statement is narrow: the hook deterministically enforces its
declared invariants over its declared inputs at its declared boundary.

### [Slide 6] Deterministic is not infallible — 4:45–5:35

Code can be wrong. A `>` where policy requires `>=` creates a consistent but
incorrect decision. A hook registered for one endpoint but not another leaves
a bypass. A check performed long before the write may use stale state.

That is why deterministic controls need exact specifications, boundary tests,
integration tests, and observable wiring. Consistency makes them easier to test
and audit; it does not remove the need for testing.

For shared mutable systems, the check and mutation may need a transaction,
lock, state-version precondition, or atomic conditional operation. Otherwise
state can change after the hook passes but before the tool writes.

### [Slide 7] The module promise — 5:35–6:00

This module will not try to make the entire agent predictable. It will identify
known failure classes and place exact controls where they can prevent effects.

Next, we will locate that point inside the model and tool lifecycle, and show
why before execution is different from evaluation after execution.

## Demonstration cue

Show `check_rollback_target_last_known_good()` in `demo/hooks.py` beside the
same target values in `scenarios/unsafe_remediation.json` and
`scenarios/valid_rollback.json`.

## Transition line

> Determinism becomes useful when the check is attached to the one boundary an
> invalid action cannot bypass.
