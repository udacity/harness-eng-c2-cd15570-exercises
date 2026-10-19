# Diagram Concepts

## D1 — Probabilistic proposal, deterministic gate

**Purpose:** State the module's core architecture.

- Model emits different possible tool proposals.
- All protected proposals enter the same solid hook boundary.
- Fixed proposal plus trusted state produces a repeatable allow/block result.

Use dotted arrows for model behavior and solid arrows for harness execution.

## D2 — Deterministic decision context

**Purpose:** Make hidden inputs visible.

```text
tool + canonical args + trusted snapshot + execution history
     + policy version + code version
                         |
                         v
                 deterministic decision
```

Place clock, network, randomness, and mutable globals outside the box with the
label “must be captured or excluded.”

## D3 — Proposal-to-effect state machine

**Purpose:** Separate evidence states.

```text
REQUESTED -> PARSED -> AUTHORIZED -> ALLOWED -> EXECUTED -> VERIFIED
                |          |           |
              ERROR      DENIED      BLOCKED
```

Do not allow a visual arrow directly from requested to executed.

## D4 — Hook versus antidote versus tool

**Purpose:** Clarify course terminology.

- Hook: socket labeled `before_tool_call`.
- Antidotes: small predicate modules inserted into the socket.
- Tool: state-changing action after the gate.

## D5 — Failure-to-antidote pipeline

**Purpose:** Teach repeatable design.

```text
observed failure
 -> explicit invariant
 -> protected boundary
 -> trusted inputs
 -> pure predicate
 -> violation evidence
 -> tests + residual risk
```

## D6 — Skills versus deterministic hooks

**Purpose:** Preserve Module 2 boundary.

- Skill lane: instructions influence the proposed rollback target.
- Hook lane: trusted state determines whether that proposal may execute.
- A skill arrow is dotted; hook gate is solid.

## D7 — Antidote matrix

**Purpose:** Connect known failures to concrete checks.

Rows: stale health, missing target, non-LKG target, repeat, premature
resolution, excessive meal, approval threshold, duplicate receipt, total
mismatch, nonpositive amount.

Columns: failure, invariant, trusted field, predicate, violation code, test.

## D8 — Exact-threshold number lines

**Purpose:** Expose comparison semantics.

- Meal: green through `100.00`, red from `100.01`.
- Approval: no approval required through `500.00`, required from `500.01`.
- Total: exact point equality; one-cent values on both sides fail.

## D9 — Complete before-tool flow

**Purpose:** Show correct ordering.

```text
parse -> resolve trusted identity/state -> permission -> safety hook
      -> conditional/atomic tool -> postcondition -> tool result
```

Apply “Module 4” label to permission and “production strengthening” to atomic
execution.

## D10 — Replay and idempotency

**Purpose:** Explain retry-safe side effects.

Two semantically equivalent calls map to one canonical signature. First call
records the effect and key; retry finds key and returns prior/blocked result.

## D11 — Evidence freshness

**Purpose:** Show why a new state invalidates old observations.

Timeline:

```text
health snapshot at state v17 -> hook allow -> mutation to v18
                                      old health snapshot becomes stale
```

## D12 — TOCTOU gap

**Purpose:** Explain shared-state race risk.

Show hook checking version 17, a concurrent actor writing version 18, and the
tool attempting a version-17-dependent mutation. Resolve with compare-and-swap
or transaction.

## D13 — Test evidence layers

**Purpose:** Avoid overclaiming from one test type.

- pure predicate truth tables;
- property and state-machine tests;
- dispatcher/spy integration tests;
- bypass and concurrency tests;
- live model orchestration runs;
- production monitoring.

## D14 — Reliability funnel

**Purpose:** Monitor execution integrity.

Protected proposals flow into hook invocations, then allow/block/error. Only
allows flow to tool executions. Any block/error-to-execution arrow is a critical
escape.
