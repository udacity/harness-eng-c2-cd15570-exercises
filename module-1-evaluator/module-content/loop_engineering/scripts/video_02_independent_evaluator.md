# Video 2 — Separate the Generator from the Evaluator

**Target duration:** 6 minutes 15 seconds  
**Learning objective:** Assign generation, evaluation, and control to separate
responsibilities and contexts.

## Instructor narration

### [Slide 1] One task, three jobs — 0:00–0:50

Suppose the candidate update from the previous lesson is sitting in memory.
Who should decide what happens next?

There are actually three jobs hiding inside that question. Someone must produce
the candidate. Someone must test it against the requirements. And something
must decide whether to accept, retry, escalate, or stop.

Production harnesses become easier to reason about when those jobs are named
and separated: generator, evaluator, and controller.

### [Slide 2] The generator owns candidates — 0:50–1:35

The generator receives the user request, relevant task context, and writing or
solution instructions. It produces a candidate. If the controller asks for a
revision, the generator receives specific findings and produces a new
candidate.

The generator should not declare its own candidate accepted. It may explain
what it tried to do, but that explanation is not the acceptance record.

In our incident example, the generator sees the authoritative `INC-2048`
snapshot and the request for a 60-word stakeholder update. Its output is a
candidate until the harness completes every required check.

### [Slide 3] The evaluator owns findings — 1:35–2:30

The evaluator receives the original requirements, the evidence relevant to
those requirements, and the candidate itself. It receives its own instructions
and returns named decisions.

For example:

```json
{
  "factual_grounding": {
    "passed": false,
    "evidence": "Candidate claims rollback; incident.rollback_performed=false",
    "feedback": "Remove the rollback and recovery claims."
  }
}
```

That finding is useful because it identifies the criterion, cites the conflict,
and tells the revision path what must change. “Needs improvement” is not enough.

The evaluator does not accept the generator's statement that a rollback
happened. It compares the statement with authoritative state.

### [Slide 4] The controller owns the stop decision — 2:30–3:25

The controller orchestrates both calls. It runs deterministic checks, requests
inferential review, parses the results, and combines them according to an
acceptance rule.

It also owns the operational boundaries that models should not control:

- maximum attempts;
- token and monetary budgets;
- quality thresholds;
- malformed-output handling;
- logging;
- and escalation.

If the evaluator returns malformed JSON, the controller fails closed or retries
the evaluation. If the third candidate still fails, the controller records a
terminal failure. It does not ask the generator to declare victory.

### [Slide 5] What independence means — 3:25–4:30

Independent evaluation does not necessarily require a different model. We can
use the same model name in two fresh calls and still separate responsibilities:

- different instructions;
- no inherited generator conversation;
- explicit evaluation evidence;
- and a controller-owned acceptance rule.

That is process independence, not statistical independence. The two calls can
still share training data, model tendencies, or blind spots. A separate model
can reduce some correlation, but it can introduce different biases and cost.

So cross-model evaluation is an optional experiment, not the definition of
generator–evaluator separation.

In the Module 1 demo, self-review continues with the candidate response ID.
Independent review starts with no previous response ID. Feedback then returns
to the candidate branch for revision rather than extending the evaluator's
conversation.

### [Slide 6] The GAN analogy—and its limit — 4:30–5:20

There is a useful structural analogy to adversarial systems. One component
produces an artifact, while another applies a discriminating signal. That
tension can drive improvement.

But this harness is not a generative adversarial network. We are not jointly
training two neural networks through a minimax objective and backpropagation.
We are orchestrating inference-time calls with explicit business criteria.

Use the analogy to remember the separation of roles. Do not use it to make
claims about the training algorithm.

### [Slide 7] Compare the two paths — 5:20–6:00

Put the two designs side by side.

```text
self-review
request -> generator -> candidate -> same conversation reviews -> stop/revise

separated evaluation
request -> generator -> candidate -> fresh evaluator -> structured findings
                                      |                  |
                                      +---- controller --+
                                             |
                                       accept/retry/fail
```

The separated design gives us an evaluation boundary we can inspect and test.
It does not guarantee truth. It gives us a place to attach better evidence.

### [Slide 8] Transition — 6:00–6:15

The architecture now has the right responsibilities, but the evaluator still
needs a definition of success. Next, we will turn vague quality goals into
deterministic and inferential criteria.

## Technical example

```python
candidate = generator.generate(request, evidence)
exact = run_deterministic_checks(candidate, requirements)
semantic = evaluator.review(request, evidence, candidate)
decision = controller.combine(exact, semantic)
```

The code is intentionally incomplete here. Video 4 adds retries, budgets,
failure handling, and logging.

## Transition line

> Separation creates an evaluation boundary. Criteria determine whether that
> boundary produces useful evidence or merely another opinion.
