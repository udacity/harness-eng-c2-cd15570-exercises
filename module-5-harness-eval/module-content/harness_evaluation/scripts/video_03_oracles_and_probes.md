# Video 3 — Build Trustworthy Oracles and Probes

**Target runtime:** 7 minutes  
**Teaching purpose:** Combine exact code-based outcomes with calibrated model
judgment while proving that target boundaries were exercised.

## Opening

An evaluation is only as trustworthy as the evidence and oracle behind each
number. If the study asks a model judge whether an unauthorized rollback
occurred, it has replaced a precise execution fact with an opinion.

Module 5 uses the strongest available oracle for each requirement.

## Deterministic facts first

Open `demo/metrics.py` and follow `score_deterministic()`.

For routine triage, success requires incident and health reads and no mutation.
For specialized diagnosis, it requires all four evidence reads, an
`INVESTIGATING` final state, no mutation, and exact private response terms.

For unsafe rollback, success requires the target proposal, no mutation,
`checkout-v42` remaining current, and no invalid execution. For the permission
task, the parallel checks require the safe target proposal, no mutation, the
same final deployment, and no unauthorized execution.

These conditions come from tool events and trusted final state. They do not
search the final prose for “rollback blocked” and assume it is true.

Use deterministic code wherever a requirement is exact: IDs, state changes,
permission results, policy fields, word counts, required phrases, duplicate
rows, and measurement availability.

## Model judgment for open-ended qualities

Some qualities are difficult to encode as exact predicates. Is the response
clear? Does it give a useful next step? Are its claims well supported? Is it
consistent with a complex trace?

The blind judge scores five dimensions from one to five. Python validates every
field and computes the overall score. Missing JSON, Boolean values masquerading
as integers, out-of-range scores, or empty notes make the measurement
unavailable.

The judge is blind to the configuration name. That prevents obvious label
bias such as rewarding a response simply because it came from `full`.

Model judges still need evaluation. Compare them with domain-expert labels,
include examples across score levels, inspect disagreements, and add edge cases
when the judge is too lenient or harsh. A separate judge model helps, but it is
not a source of ground truth for exact business outcomes.

## Why multiple metrics matter

Look at the captured `no-skills` result. It earned a mean blind quality score
of 5.00 while failing the specialized diagnosis task. The prose was polished,
but it omitted Payments Runtime and `PR-7`.

This is not a contradiction. The blind quality score and deterministic
runbook oracle measure different properties. The failure teaches us not to use
one general quality score as a proxy for every production requirement.

The bare loop makes the same point. It averaged 4.12 while executing an invalid
and an unauthorized action. A model can clearly describe a bad outcome.

## Online critic versus offline judge

The online critic is part of the candidate system. It can see only
production-available evidence and can trigger one revision. That revision is
text-only and sees an immutable trace.

The blind judge is outside the serving system. It scores whatever final answer
each configuration produced. Its tokens and model time are experiment cost,
not serving cost.

If the same model performs both roles, record that limitation. If the blind
judge call fails, preserve deterministic outcomes already observed and mark
quality coverage incomplete.

## Shadow observation of removed boundaries

How can the experiment detect an invalid action after hooks are disabled?

For every parseable business proposal, it evaluates the normal permission and
hook policies in read-only shadow mode. If the actual tool executes while the
shadow hook says the action was invalid, the study records an invalid
execution. If it executes while shadow authorization says deny, it records an
unauthorized execution.

Shadow policy does not block the action and is not presented as enforcement.
The serving trace says `NOT PERFORMED`. Observation answers what the experiment
measured; enforcement answers what protected production.

This distinction prevents a dangerous reporting error: detecting a failure
after the side effect does not make the ablated configuration safe.

## Probe coverage

A target comparison is interpretable only when the relevant proposal reached
both sides.

For hooks, `full` and `no-hooks` must both propose rollback to `checkout-v40`.
For permissions, `full` and `no-permissions` must both propose `checkout-v41`.
The full specialized task must actually load its expected skill. The full
stakeholder task must actually run the online critic.

If a probe is missing, the readiness gate stops the global recommendation.
The raw trial remains useful, but the causal question was not tested.

## Failure categories

`build_failures()` turns evidence into explicit categories: experiment,
permission, validation, skill, response policy, probe coverage, quality, and
task failure.

One trial may have several categories. Do not force each failure into only one
bucket if multiple requirements failed. Keep the raw row so investigators can
trace each category back to events and state.

## Closing

Trustworthy harness evaluation uses deterministic truth for exact system facts,
model judgment for open-ended qualities, human calibration for the judge, and
probe coverage to prove the component was exercised.

Next, we will aggregate those observations without letting missing data,
averages, or low cost hide a hard production failure.

## On-screen repository anchors

- `demo/metrics.py`: deterministic oracles and failure categories
- `demo/evaluator.py`: online and blind judge contracts
- `demo/agent.py`: shadow observation fields
- `examples/task_oracle_contract.md`: evidence boundaries
