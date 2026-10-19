# Diagram Concepts

## Visual thesis

The module's recurring visual is a trial ledger. Every conclusion must trace
back through configuration, task, proposal, decisions, execution, state, and
scoring evidence.

## Concept 1 — Component switchboard

Use four physical switches labeled skills, evaluator, hooks, and permissions.
For each one-component ablation, animate exactly one switch off. Turn all four
off for `bare`, then place a “not causal” warning beside it.

## Concept 2 — Evidence stack

Stack five transparent sheets:

1. proposal;
2. enforcement;
3. execution;
4. deterministic outcome;
5. model-judged quality.

A claim can be inspected through the stack. A polished response sheet cannot
erase an execution event below it.

## Concept 3 — Target probe

Show a test signal reaching a boundary. When `checkout-v40` reaches the hook,
the probe indicator lights. When the model declines before proposing, the hook
remains gray and the indicator says “not exercised.”

## Concept 4 — Exact versus subjective oracle

Left: code ruler measures identifiers, state, executions, limits, and coverage.
Right: calibrated judge scores clarity, next step, support, and consistency.
Neither tool crosses into the other's labeled domain.

## Concept 5 — Shadow observer

Use a transparent observer booth beside the ablated execution lane. It can
write an audit label but has no gate or lever connected to the tool. This
prevents learners from confusing detection with prevention.

## Concept 6 — Coverage card

Every metric is a two-sided card:

```text
value: invalid executions = 0
coverage: 5/5 trials = 100%
```

If one side is missing, turn the whole card gray and label it unavailable.

## Concept 7 — Qualification funnel

Configuration cards pass through hard gates. Failed cards exit sideways with
reason labels. Only remaining cards reach a small cost-ranking scale.

Do not use a single weighted-score leaderboard; it suggests safety can be
traded against cost.

## Concept 8 — Scoped recommendation frame

Place the recommendation inside a frame with five metadata tabs: model, task
suite, policy/oracle version, thresholds, and repetitions. A statement extending
outside the frame fades to indicate unsupported generalization.

## Motion and semantic rules

- Amber: proposed but not executed.
- Blue: measured evidence or trusted state.
- Green: passed exact requirement or confirmed execution.
- Red: failed hard gate, invalid, or unauthorized execution.
- Purple: model-based evaluator or judge.
- Gray: disabled, not performed, unexercised, or unavailable—always with text.
- Dashed line: observation only.
- Solid gate: serving enforcement.

Never encode outcome only with color.
