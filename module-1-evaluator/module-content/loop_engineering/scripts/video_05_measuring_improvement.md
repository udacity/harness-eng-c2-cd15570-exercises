# Video 5 — Measure Whether the Evaluator Helps

**Target duration:** 6 minutes 15 seconds  
**Learning objective:** Compare quality and failure rates against an external
reference while accounting for tokens, cost, and latency.

## Instructor narration

### [Slide 1] Repetition is not improvement — 0:00–0:45

A system can loop three times, spend three times as many tokens, and finish with
the same mistake. Iteration count is activity, not value.

To justify an evaluator, compare the output before and after evaluation against
a reference that neither path controls: unit tests, verified incident facts,
expert labels, or instructor-reviewed examples.

The question is not “Did the evaluator produce feedback?” The question is “Did
the complete system make better acceptance decisions and better final outputs?”

### [Slide 2] Use the same representative cases — 0:45–1:35

Compare two implementations on the same case set:

```text
A. generator + same-conversation self-evaluation
B. generator + independent evaluation
```

Hold the task inputs, generation model, sampling policy, attempt limits, and
reference standard constant where possible. Run enough repeated samples to
observe variability. Do not compare one lucky external run with one unlucky
self-review run.

The Module 1 demo is a qualitative classroom example. A production decision
needs a broader held-out set: grounded and ungrounded updates, exact-format
failures, subtle omissions, and cases that should pass without revision.

### [Slide 3] Measure output quality and decisions — 1:35–2:35

Track initial and final quality using the same rubric. Then measure the
acceptance decision itself.

Acceptance rate is the fraction of cases the harness accepts. High acceptance
is not necessarily good.

False acceptance occurs when the harness accepts an output that the reference
standard says is unacceptable. For high-impact output, this is often the most
important error.

False rejection occurs when the harness rejects an acceptable output. That
hurts throughput and can cause unnecessary revisions or escalation.

Use the reference-unacceptable cases as the denominator for false acceptance,
and reference-acceptable cases as the denominator for false rejection. State
the denominators so readers cannot confuse the rates.

### [Slide 4] Measure operational cost — 2:35–3:25

Quality is only half of the decision. Record:

- generator and evaluator calls;
- iterations;
- input and output tokens;
- evaluator tokens separately;
- estimated or billed cost;
- time to first candidate;
- total latency; and
- escalation rate.

Then calculate a useful efficiency measure such as quality gain per thousand
additional tokens or false acceptances prevented per dollar.

Do not hide evaluation overhead inside one total. Teams need to know what the
extra boundary costs and what it buys.

### [Slide 5] Read an illustrative comparison — 3:25–4:20

The table on screen is synthetic. It demonstrates calculations; it is not a
benchmark claim.

In this illustration, the reference set contains 20 cases: 12 acceptable and 8
unacceptable. Self-evaluation falsely accepts 5 of the 8 bad cases. Independent
evaluation falsely accepts 1. That is a reduction in false acceptance from
62.5 percent to 12.5 percent.

Independent evaluation also falsely rejects 2 good cases instead of 1, uses
more evaluator tokens, and adds latency. The result is not “external always
wins.” It is a concrete tradeoff: much stronger rejection of bad outputs at the
cost of some throughput and serving overhead.

The product owner must decide whether that tradeoff matches the risk of the
task.

### [Slide 6] Calibrate the evaluator — 4:20–5:05

An evaluator should be evaluated.

Review disagreements against the reference. Test order changes for position
bias. Include concise and verbose answers. Include outputs from the evaluator's
own model and from other models. Inspect malformed responses and ambiguous
rubric cases.

If an exact check can replace an unreliable semantic judgment, prefer the exact
check. If one inferential criterion causes most false rejections, refine that
criterion or route it to a human. If a separate model reduces correlated error
enough to justify its cost, adopt it based on evidence.

### [Slide 7] Know when not to add an evaluator — 5:05–5:45

Do not add an LLM evaluator merely because evaluation sounds mature.

Deterministic verification may be sufficient when success is completely
captured by tests, schemas, constraints, or trusted state transitions. An
evaluator may also be unnecessary for low-risk drafts that a human always
reviews, or when latency and cost exceed the value of automatic filtering.

Sometimes the best design is a narrow evaluator used only for high-risk or
ambiguous cases rather than every response.

### [Slide 8] Final principle — 5:45–6:15

The goal is not to make the agent repeat its work until it feels confident.
The goal is to provide evidence that the completed work satisfies the
requirements.

Separate responsibilities. Use exact checks where possible. Calibrate judgment
where necessary. Bound the loop. Preserve failures. And measure whether the
added machinery improves the outcomes that matter.

That is loop engineering in the harness.

## Measurement formulas

```text
acceptance_rate = accepted_cases / all_cases

false_acceptance_rate =
    accepted_but_reference_unacceptable / reference_unacceptable

false_rejection_rate =
    rejected_but_reference_acceptable / reference_acceptable

quality_gain_per_1k_extra_tokens =
    (mean_final_quality - mean_initial_quality) / (extra_tokens / 1000)
```

## Closing line

> Confidence may be useful context. Evidence is what earns acceptance.
