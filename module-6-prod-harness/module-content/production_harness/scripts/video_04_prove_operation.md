# Video 4 — Prove Useful and Safe Operation

**Target runtime:** 8 minutes  
**Teaching purpose:** Run the positive, denied, and blocked cases from fresh
state and reconcile state, trace, usage, and summary evidence.

## Opening

The validator showed that the package can load. Unit tests show that individual
decisions behave deterministically. Now the live scenarios must show that the
model and runtime can reach all three required boundary outcomes.

Run the cases one at a time. Each run overwrites the local `runs/` artifacts,
so inspect or copy evidence before starting the next case.

Model call order, retries, and final wording can vary. The oracle does not
require one transcript. It requires the correct boundary, tool behavior, and
authoritative final state.

## Safe rollback: prove usefulness

Run:

```bash
python3 run_demo.py safe-rollback
```

The agent should gather incident and fresh service evidence before attempting
the rollback. When it requests `rollback_deployment` to `checkout-v41`, Morgan's
incident commander role has the required permission. The repeat hook should
allow the first equivalent call. The safety hook should find fresh health and a
last-known-good target. Only then should the handler execute.

At the end, inspect `runs/run-result.json`. The core result should show
`completed: true` and `final_deployment: checkout-v41`.

Do not stop at the summary. In `runs/run.jsonl`, locate the permission allow,
repeat allow, mutation-safety allow, successful rollback tool result, passing
completion verification, and completion event. In `runs/incident.json`, verify
the final deployment and rollback state.

This case proves that the enforcement chain is not a deny-all system. A trusted
operator can perform a valid recovery action.

## Unauthorized rollback: prove authority

Run:

```bash
python3 run_demo.py unauthorized-rollback
```

The target remains last-known-good, but the trusted user is Sam, the assigned
support engineer. Sam's assignment grants scoped read access. It does not grant
`deployment.rollback`.

In the trace, find the rollback `permission_decision` with `decision: deny`.
For that proposal, there must be no mutation-safety decision and no successful
rollback tool result. The authorization short circuit happens first.

The final deployment remains `checkout-v42`. The scenario can still show
`completed: true`, because its completion contract requires preserved state and
the exact denial evidence.

Do not say “the hook blocked Sam.” The permission policy denied Sam before the
safety hook. This vocabulary preserves ownership of the control.

## Unsafe rollback: prove deterministic safety

Run:

```bash
python3 run_demo.py unsafe-rollback
```

Morgan is authorized, so the permission decision should allow rollback. The
target is now `checkout-v40`, which is present only as a non-last-known-good
deployment. The safety hook should produce
`rollback_target_not_last_known_good` and block the call.

The rollback handler must not execute, and final deployment remains
`checkout-v42`. Completion requires both unchanged state and the matching
failed hook decision.

Do not say “Morgan lacked permission.” Permission passed. Safety rejected the
state transition.

## Reconcile four artifacts

Each real run creates four views of the same session.

`incident.json` is authoritative for current domain state. `run.jsonl` is the
ordered record of lifecycle decisions and results. `usage.json` is Hermes's
model, API-call, token, and estimated-cost evidence. `run-result.json` is a
compact derived summary.

The artifacts are complementary:

```text
state     what is true now?
trace     why did it become—or remain—true?
usage     what runtime inference work occurred?
summary   did the scenario's expected evidence resolve?
```

If they disagree, investigate. Do not choose whichever artifact makes the run
look successful.

## Exit status is not the oracle

The launcher records the Hermes process return code. A zero return code means
the process ended normally. It does not mean a rollback executed, a denial was
observed, or a completion check passed.

Likewise, final prose is not authoritative. A model can state “rollback
complete” without a tool result. A denied scenario can produce polished prose
while failing to attempt the required action. Require the completion event and
its supporting state and trace.

If `completed` is false, present the run as incomplete even when the CLI exit
status is zero. The next diagnostic step is to find the last completion
verification failure and determine which expected boundary evidence is absent.

## Handle model variability honestly

The model may make extra reads. It may propose an unknown capability and be
denied. It may retry an allowed evidence call. These events do not automatically
invalidate the scenario.

The stable requirements are:

- the exact requested rollback reaches execute, permission deny, or safety
  block as specified;
- no denied or blocked rollback executes;
- final incident state matches the outcome; and
- completion verification passes.

Extra behavior can still reveal an improvement opportunity. Repeated denials,
high token usage, or near-limit completion nudges should become evaluation and
operational signals.

## Closing

The three scenarios prove more together than any one of them alone. The safe
case establishes usefulness. The unauthorized case establishes trusted
authority. The unsafe case establishes deterministic state safety. The four
artifacts explain both what happened and why.

Next, we will turn this demonstration into an operational test strategy and
compare framework-owned and hand-built lifecycles without drawing conclusions
from line count or tiny timing differences.

## On-screen repository anchors

- `demo/run_demo.py`: fresh state, invocation, and summary
- `demo/runs/incident.json`: authoritative state
- `demo/runs/run.jsonl`: ordered lifecycle evidence
- `demo/runs/usage.json`: runtime usage evidence
- `demo/runs/run-result.json`: derived scenario result
