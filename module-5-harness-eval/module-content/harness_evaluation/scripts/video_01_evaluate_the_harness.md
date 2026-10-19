# Video 1 — Evaluate the Harness, Not Only the Model

**Target runtime:** 6 minutes  
**Teaching purpose:** Establish the system-level unit of analysis and the facts
that a harness evaluation must keep separate.

## Opening

Modules 1 through 4 built a production loop one boundary at a time. Module 5
asks the engineering question that follows: which components measurably improve
the system enough to justify their cost?

The answer cannot come from intuition, component count, or one impressive
transcript. It needs an evaluation of the entire harness.

## Model evaluation versus harness evaluation

Model evaluation asks whether the model understood a request, selected a useful
action, and wrote a good answer.

Harness evaluation asks what the surrounding system added. Did a skill supply
private knowledge? Did authorization stop an unauthorized action? Did a hook
stop an invalid mutation? Did an online critic repair a response-policy failure?
What did each addition cost on the serving path?

A strong model can still benefit from an execution guarantee. A failed result
does not prove that every component is valuable. We need to measure each
component's distinct contribution.

The Module 5 principle is:

> No component without an eval.

That principle cuts both ways. Do not retain a component merely because it
sounds responsible. Do not remove a control merely because the model behaved
well in one example.

## Five facts, not one score

Open `demo/agent.py` and `demo/experiment.py`. One trial produces several
different kinds of evidence.

First, the model proposes a tool. A proposal is not execution.

Second, permissions allow or deny the authenticated subject. Third, a hook
allows or blocks an authorized mutation. Fourth, the dispatcher either runs or
does not run, and trusted state may change. Finally, an evaluator observes the
response and trace.

These stages answer different questions:

```text
proposal     what did the model request?
enforcement what did permissions and hooks decide?
execution   what side effect actually occurred?
evaluation  how well did the final response satisfy criteria?
```

If a response says, “Rollback complete,” only the dispatcher event and final
incident state can establish whether that happened. A fluent claim cannot
override a denied or blocked call.

## The cumulative harness

The system under evaluation has four switches.

Skills add scoped instructions and private service knowledge before a decision.
Permissions decide whether the trusted subject may attempt an action on the
resource. Hooks check deterministic state invariants immediately before a
mutation. The online evaluator reviews a candidate and can request one
text-only revision.

The evaluator is intentionally last. Its revision has no tools. It can repair
an explanation, but it cannot undo a rollback, repeat a blocked action, or
authorize a user.

The business boundary remains:

```text
proposal -> permission -> hook -> tool
```

The study must preserve that execution truth while switching components on and
off.

## Define success before measuring

A harness is not successful simply because the model returned text. The
incident demo requires complete task success, no invalid execution, no
unauthorized execution, acceptable minimum blind quality, full measurement
coverage, and exercised component probes.

These are multiple gates, not ingredients in one average. Zero unauthorized
actions is not a score that poor prose can offset. High prose quality cannot
compensate for an unsafe side effect. Low cost cannot compensate for a failed
production requirement.

The exact thresholds belong to the application. The incident demo requires
100 percent task success. The returns exercise declares 90 percent. Students
must read and justify the threshold for the system under evaluation rather
than assume one universal number.

## Separate serving from measurement

The online critic is part of the deployed path when enabled. Its model calls,
tokens, and latency count as serving cost.

The blind offline judge is an experiment instrument. It scores all
configurations after serving. It does not change the answer or execute tools,
and its cost is recorded as benchmark overhead.

Without that separation, a configuration containing the online evaluator could
appear artificially cheap, or every configuration could be charged for an
offline judge that production users never invoke.

## The optimization objective

The goal is not automatically `full`. It is the smallest configuration that
meets every declared requirement with complete evidence.

That means qualification comes first. Cost optimization comes second. If two
configurations both qualify, prefer fewer enabled components, then lower
measured serving tokens and model seconds. If only one qualifies, it wins even
if another is cheaper.

## Closing

Module 5 evaluates a production system, not a single answer. It records what
the model proposed, what the harness enforced, what the tool executed, what
state resulted, and what the evaluator observed.

Next, we will construct the comparisons that can attribute an observed change
to one component rather than four changing at once.

## On-screen repository anchors

- `demo/agent.py`: switched components and execution trace
- `demo/experiment.py`: one trial and cost boundaries
- `demo/metrics.py`: deterministic outcomes and qualification
- `demo/config.py`: six configurations
